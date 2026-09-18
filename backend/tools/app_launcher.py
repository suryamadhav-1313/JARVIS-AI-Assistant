"""
app_launcher.py
----------------
Opens applications that are registered in an explicit whitelist OR
safely discovered from Windows Start Menu shortcuts.

Safety rules:
- JARVIS can ONLY launch apps that appear in APP_WHITELIST below OR
  are safely discovered via Windows Start Menu shortcuts.
- There is no way to pass an arbitrary command line or shell string in -
  callers pass a canonical key (e.g. "vscode"), never a raw string that
  reaches a shell.
- On Windows this uses os.startfile (no shell involved). For apps that
  register a URI protocol (e.g. Spotify's "spotify:" links), that protocol
  is tried first via os.startfile - this is the standard, safe way Windows
  itself launches "app-like" targets without needing a hardcoded exe path.
  If no protocol is registered or it fails, it falls back to a fixed
  executable name, which Windows resolves via PATH / the "App Paths"
  registry key - still no shell string is built or executed.
- On macOS/Linux this falls back to `subprocess.Popen([...])` with a fixed
  argument list (still not a shell command, no string concatenation).
- Discovered apps are validated: they must be .lnk shortcuts in standard
  Start Menu locations pointing to .exe files. Arbitrary paths are NEVER
  executed directly from user input.

To add a new whitelisted app: add an entry to APP_WHITELIST and, optionally,
some friendly names to APP_ALIASES pointing at its canonical key. Never add
anything that accepts user-supplied arguments or builds a command string
from user input.
"""

import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set
from functools import lru_cache


@dataclass
class AppTarget:
    display: str  # human-friendly name used in replies, e.g. "VS Code"
    # A URI scheme to try first via os.startfile, e.g. "spotify:" or "whatsapp:".
    # Used for apps that register a protocol handler - this is a safe,
    # fixed string, never built from user input.
    protocol: Optional[str] = None
    # Executable name/path used on Windows (os.startfile). Windows resolves
    # bare names like "Spotify.exe" via PATH or the registry "App Paths" key.
    windows: Optional[str] = None
    # Fixed argument list used on macOS, e.g. ["open", "-a", "Spotify"]
    macos: Optional[list] = None
    # Fixed argument list used on Linux, e.g. ["xdg-open", "spotify"]
    linux: Optional[list] = None
    # For discovered apps: the full path to the .lnk shortcut
    shortcut_path: Optional[str] = None


# Explicit whitelist of apps JARVIS is allowed to open.
# Extend this dictionary as needed - nothing outside this map (and the
# discovered apps cache) can be launched.
APP_WHITELIST: Dict[str, AppTarget] = {
    "notepad": AppTarget(display="Notepad", windows="notepad.exe", linux=["xdg-open", "gedit"]),
    "calculator": AppTarget(
        display="Calculator", windows="calc.exe", macos=["open", "-a", "Calculator"]
    ),
    "explorer": AppTarget(
        display="File Explorer",
        windows="explorer.exe",
        macos=["open", "."],
        linux=["xdg-open", "."],
    ),
    "paint": AppTarget(display="Paint", windows="mspaint.exe"),
    "chrome": AppTarget(
        display="Chrome",
        windows="chrome.exe",
        macos=["open", "-a", "Google Chrome"],
        linux=["xdg-open", "google-chrome"],
    ),
    "cmd": AppTarget(display="Command Prompt", windows="cmd.exe"),
    "vscode": AppTarget(
        display="VS Code",
        windows="code",
        macos=["open", "-a", "Visual Studio Code"],
        linux=["code"],
    ),
    "spotify": AppTarget(
        display="Spotify",
        protocol="spotify:",
        windows="Spotify.exe",
        macos=["open", "-a", "Spotify"],
        linux=["xdg-open", "spotify"],
    ),
    "discord": AppTarget(
        display="Discord",
        windows="Discord.exe",
        macos=["open", "-a", "Discord"],
        linux=["xdg-open", "discord"],
    ),
    "whatsapp": AppTarget(
        display="WhatsApp",
        protocol="whatsapp:",
        windows="WhatsApp.exe",
        macos=["open", "-a", "WhatsApp"],
        linux=["xdg-open", "whatsapp"],
    ),
}

# Friendly aliases -> canonical APP_WHITELIST key.
# Matching is always done in lowercase (see resolve_app_alias).
# This includes both whitelisted apps and common names for discovered apps.
APP_ALIASES: Dict[str, str] = {
    # notepad
    "notepad": "notepad",
    # calculator
    "calculator": "calculator",
    "calc": "calculator",
    # explorer / file explorer
    "explorer": "explorer",
    "file explorer": "explorer",
    "windows explorer": "explorer",
    "files": "explorer",
    # paint
    "paint": "paint",
    "ms paint": "paint",
    # chrome
    "chrome": "chrome",
    "google chrome": "chrome",
    "chrome browser": "chrome",
    # cmd
    "cmd": "cmd",
    "command prompt": "cmd",
    "terminal": "cmd",
    # vscode
    "vscode": "vscode",
    "vs code": "vscode",
    "visual studio code": "vscode",
    "code": "vscode",
    # spotify
    "spotify": "spotify",
    # discord
    "discord": "discord",
    # whatsapp
    "whatsapp": "whatsapp",
    "whats app": "whatsapp",
    "whatsapp desktop": "whatsapp",
    # edge
    "edge": "edge",
    "microsoft edge": "edge",
    # firefox
    "firefox": "firefox",
    "mozilla firefox": "firefox",
    # steam
    "steam": "steam",
    # epic games
    "epic games": "epic games",
    "epic games launcher": "epic games",
    # common apps
    "slack": "slack",
    "teams": "teams",
    "microsoft teams": "teams",
    "zoom": "zoom",
    "outlook": "outlook",
    "word": "word",
    "excel": "excel",
    "powerpoint": "powerpoint",
    "onenote": "onenote",
    # games
    "minecraft": "minecraft",
    "valorant": "valorant",
    "gta": "gta",
    "gta v": "gta",
    "roblox": "roblox",
    "league of legends": "league of legends",
    "overwatch": "overwatch",
    "battle.net": "battle.net",
    "blizzard": "battle.net",
    # leetcode desktop (if installed)
    "leetcode desktop": "leetcode desktop",
    # browsers
    "brave": "brave",
    "opera": "opera",
    "vivaldi": "vivaldi",
}

# Canonical keys for system apps that have fixed launch behavior.
# These are handled specially in open_app().
_SYSTEM_APP_KEYS = {
    "explorer",
    "notepad",
    "calculator",
    "paint",
    "cmd",
}

# Cache for discovered applications
_discovered_apps_cache: Optional[Dict[str, AppTarget]] = None
_discovered_aliases_cache: Optional[Dict[str, str]] = None


def _get_start_menu_paths() -> List[Path]:
    """Return a list of Start Menu program directories to scan for shortcuts."""
    paths: List[Path] = []

    # Current user's Start Menu Programs
    appdata = os.environ.get("APPDATA")
    if appdata:
        paths.append(Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs")

    # All users' Start Menu Programs
    programdata = os.environ.get("PROGRAMDATA")
    if programdata:
        paths.append(Path(programdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs")

    # Also check the modern Windows 10/11 locations
    localappdata = os.environ.get("LOCALAPPDATA")
    if localappdata:
        # Windows Apps folder (UWP apps)
        paths.append(Path(localappdata) / "Microsoft" / "WindowsApps")

    return paths


def _resolve_shortcut_target(shortcut_path: Path) -> Optional[Path]:
    """
    Resolve a .lnk shortcut to its target executable.
    Returns the target Path if it's an .exe file, None otherwise.
    """
    try:
        # Use Windows COM to resolve the shortcut
        import win32com.client  # type: ignore

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        target = shortcut.Targetpath
        if target and target.lower().endswith(".exe"):
            target_path = Path(target)
            if target_path.exists():
                return target_path
    except Exception:
        # win32com not available or shortcut resolution failed
        pass
    return None


def _discover_windows_apps() -> Dict[str, AppTarget]:
    """
    Scan Windows Start Menu for .lnk shortcuts and build a dictionary of
    discovered applications. Returns {canonical_key: AppTarget}.
    """
    apps: Dict[str, AppTarget] = {}
    seen_executables: Set[str] = set()

    start_menu_paths = _get_start_menu_paths()

    for start_menu in start_menu_paths:
        if not start_menu.exists():
            continue

        # Walk all .lnk files recursively
        for shortcut_path in start_menu.rglob("*.lnk"):
            try:
                target_exe = _resolve_shortcut_target(shortcut_path)
                if not target_exe:
                    continue

                # Use the executable name (without .exe) as the base key
                exe_name = target_exe.stem.lower()

                # Skip system/utility executables that aren't user-facing apps
                if exe_name in {
                    "uninstall",
                    "unins000",
                    "setup",
                    "install",
                    "update",
                    "updater",
                    "crashpad_handler",
                    "chrome_proxy",
                    "msedge_proxy",
                }:
                    continue

                # Deduplicate by executable path
                exe_str = str(target_exe).lower()
                if exe_str in seen_executables:
                    continue
                seen_executables.add(exe_str)

                # Create a clean canonical key from the shortcut name
                shortcut_name = shortcut_path.stem
                canonical_key = _normalize_app_key(shortcut_name)

                # If we already have this key from a different shortcut, make it unique
                base_key = canonical_key
                counter = 1
                while canonical_key in apps:
                    counter += 1
                    canonical_key = f"{base_key}_{counter}"

                apps[canonical_key] = AppTarget(
                    display=shortcut_name,
                    windows=str(target_exe),
                    shortcut_path=str(shortcut_path),
                )
            except Exception:
                # Skip any shortcut that causes issues
                continue

    return apps


def _normalize_app_key(name: str) -> str:
    """Normalize an app name to a canonical key: lowercase, alphanumeric + underscore."""
    import re
    # Replace non-alphanumeric with underscore, collapse multiple underscores
    key = re.sub(r"[^a-z0-9]+", "_", name.lower())
    key = re.sub(r"_+", "_", key).strip("_")
    return key


def _build_discovered_aliases(discovered_apps: Dict[str, AppTarget]) -> Dict[str, str]:
    """Build alias mappings for discovered apps."""
    aliases = {}
    for key, target in discovered_apps.items():
        # Primary alias: the display name (e.g. "Discord")
        aliases[target.display.lower()] = key

        # Also add normalized versions
        normalized_display = _normalize_app_key(target.display)
        if normalized_display != key:
            aliases[normalized_display] = key

        # Add the canonical key itself
        aliases[key] = key

        # Add the executable name without extension
        if target.windows:
            exe_name = Path(target.windows).stem.lower()
            aliases[exe_name] = key

    return aliases


def get_discovered_apps() -> Dict[str, AppTarget]:
    """Get the cached discovered applications, scanning if necessary."""
    global _discovered_apps_cache
    if _discovered_apps_cache is None:
        if platform.system() == "Windows":
            _discovered_apps_cache = _discover_windows_apps()
        else:
            _discovered_apps_cache = {}
    return _discovered_apps_cache


def get_discovered_aliases() -> Dict[str, str]:
    """Get the cached discovered aliases, building if necessary."""
    global _discovered_aliases_cache
    if _discovered_aliases_cache is None:
        _discovered_aliases_cache = _build_discovered_aliases(get_discovered_apps())
    return _discovered_aliases_cache


def clear_discovery_cache() -> None:
    """Clear the discovered apps cache (useful for testing)."""
    global _discovered_apps_cache, _discovered_aliases_cache
    _discovered_apps_cache = None
    _discovered_aliases_cache = None


def list_available_apps() -> List[str]:
    """Return the canonical keys of all apps JARVIS currently knows how to open."""
    whitelisted = set(APP_WHITELIST.keys())
    discovered = set(get_discovered_apps().keys())
    return sorted(whitelisted | discovered)


def resolve_app_alias(name: str) -> Optional[str]:
    """
    Look up a free-text app name (case-insensitive) and return its canonical
    key (either from whitelist or discovered apps), or None if not recognized.
    Read-only lookup - performs no OS action.
    """
    if not name:
        return None

    normalized = name.strip().lower()

    # Check explicit whitelist aliases first
    if normalized in APP_ALIASES:
        return APP_ALIASES[normalized]

    # Check discovered apps aliases
    discovered_aliases = get_discovered_aliases()
    if normalized in discovered_aliases:
        return discovered_aliases[normalized]

    return None


class AppLaunchError(Exception):
    pass


def open_app(canonical_key: str) -> dict:
    """
    Open an application by its CANONICAL key (must be in APP_WHITELIST or
    discovered apps - use resolve_app_alias() first to turn free text into
    a canonical key).

    Returns {"display": <friendly name>}.
    Raises AppLaunchError if the key is not recognized or launch fails.
    """
    key = (canonical_key or "").strip().lower()

    # Check whitelist first
    target = APP_WHITELIST.get(key)

    # Check discovered apps
    if target is None:
        discovered = get_discovered_apps()
        target = discovered.get(key)

    if target is None:
        available = ", ".join(list_available_apps())
        raise AppLaunchError(
            f"'{canonical_key}' is not in the allowed app list. "
            f"Available apps: {available}"
        )

    system = platform.system()

    try:
        if system == "Windows":
            launched = False
            # Try the protocol handler first (safe, fixed string - no shell).
            if target.protocol:
                try:
                    os.startfile(target.protocol)  # type: ignore[attr-defined]
                    launched = True
                except OSError:
                    launched = False
            if not launched:
                if not target.windows:
                    raise AppLaunchError(f"No Windows launch target configured for '{key}'.")
                # os.startfile is a safe Windows API - it does not go through a shell.
                os.startfile(target.windows)  # type: ignore[attr-defined]

        elif system == "Darwin":
            if not target.macos:
                raise AppLaunchError(f"No macOS launch target configured for '{key}'.")
            subprocess.Popen(target.macos)

        elif system == "Linux":
            if not target.linux:
                raise AppLaunchError(f"No Linux launch target configured for '{key}'.")
            subprocess.Popen(target.linux)

        else:
            raise AppLaunchError(f"Unsupported operating system: {system}")

    except AppLaunchError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AppLaunchError(f"Failed to open '{key}': {exc}") from exc

    return {"display": target.display}