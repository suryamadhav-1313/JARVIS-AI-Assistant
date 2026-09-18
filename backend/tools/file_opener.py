"""
file_opener.py
---------------
Opens existing files and folders using safe OS APIs.

Safety rules:
- Only OPENS files/folders that already exist. Never creates, deletes,
  renames, moves, or writes to anything.
- No shell is invoked. Windows uses os.startfile; macOS/Linux use a fixed
  `open`/`xdg-open` argument list via subprocess.Popen.
- Paths are resolved and checked for existence before anything happens.
- Optionally restricted to a set of allowed root directories via
  config.settings.allowed_roots (empty by default = any existing path).
- Known user folders (Downloads, Documents, Desktop, Pictures, Videos,
  Music) are resolved from the current user's home directory - the same
  approach Windows itself uses for the default (non-redirected) location
  of these folders, e.g. C:\\Users\\<name>\\Downloads. This intentionally
  does NOT create any folder that doesn't already exist.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, Optional

from config import settings

# Friendly alias -> canonical folder key. Matched in lowercase.
FOLDER_ALIASES: Dict[str, str] = {
    "downloads": "downloads",
    "download": "downloads",
    "documents": "documents",
    "document": "documents",
    "desktop": "desktop",
    "pictures": "pictures",
    "picture": "pictures",
    "photos": "pictures",
    "videos": "videos",
    "video": "videos",
    "music": "music",
}

# Canonical folder key -> the actual sub-folder name under the user's home dir.
FOLDER_DISPLAY: Dict[str, str] = {
    "downloads": "Downloads",
    "documents": "Documents",
    "desktop": "Desktop",
    "pictures": "Pictures",
    "videos": "Videos",
    "music": "Music",
}


class FileOpenError(Exception):
    pass


def resolve_folder_alias(name: str) -> Optional[str]:
    """
    Look up a free-text folder name (case-insensitive) and return its
    canonical FOLDER_DISPLAY key, or None. Read-only lookup, no OS action.
    """
    if not name:
        return None
    return FOLDER_ALIASES.get(name.strip().lower())


def _validate_path(raw_path: str) -> Path:
    """Resolve a path and make sure it exists and is within allowed roots (if any)."""
    if not raw_path or not raw_path.strip():
        raise FileOpenError("No path was provided.")

    path = Path(raw_path).expanduser().resolve()

    if not path.exists():
        raise FileOpenError(f"Path does not exist: {path}")

    allowed_roots = settings.allowed_roots
    if allowed_roots:
        allowed = any(
            str(path).lower().startswith(str(Path(root).expanduser().resolve()).lower())
            for root in allowed_roots
        )
        if not allowed:
            raise FileOpenError(
                f"Path '{path}' is outside the allowed directories configured in .env."
            )

    return path


def _open_path(path: Path) -> None:
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]  # safe, no shell
        elif system == "Darwin":
            subprocess.Popen(["open", str(path)])
        elif system == "Linux":
            subprocess.Popen(["xdg-open", str(path)])
        else:
            raise FileOpenError(f"Unsupported operating system: {system}")
    except FileOpenError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise FileOpenError(f"Failed to open '{path}': {exc}") from exc


def open_file(file_path: str) -> dict:
    """Open an existing file with its default associated application."""
    path = _validate_path(file_path)
    if not path.is_file():
        raise FileOpenError(f"'{path}' exists but is not a file.")
    _open_path(path)
    return {"display": path.name, "path": str(path)}


def open_folder(folder_path: str) -> dict:
    """Open an existing folder (given as an explicit path) in the file explorer."""
    path = _validate_path(folder_path)
    if not path.is_dir():
        raise FileOpenError(f"'{path}' exists but is not a folder.")
    _open_path(path)
    return {"display": path.name or str(path), "path": str(path)}


def open_known_folder(canonical_key: str) -> dict:
    """
    Open one of the well-known user folders (Downloads, Documents, Desktop,
    Pictures, Videos, Music) by its CANONICAL key - use resolve_folder_alias()
    first to turn free text into a canonical key.

    Returns {"display": <friendly name>, "path": <resolved path>}.
    """
    key = (canonical_key or "").strip().lower()
    folder_name = FOLDER_DISPLAY.get(key)
    if folder_name is None:
        raise FileOpenError(
            f"'{canonical_key}' is not a recognized folder. "
            f"Known folders: {', '.join(sorted(FOLDER_DISPLAY.values()))}"
        )

    path = (Path.home() / folder_name).resolve()
    if not path.exists():
        raise FileOpenError(f"The {folder_name} folder was not found at {path}.")
    if not path.is_dir():
        raise FileOpenError(f"'{path}' exists but is not a folder.")

    _open_path(path)
    return {"display": folder_name, "path": str(path)}
