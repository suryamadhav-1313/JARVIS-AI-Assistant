"""
router.py
---------
Defines the request/response schemas for the /chat endpoint and a
deterministic, keyword/alias-based natural-language router.

This module ONLY:
    1. Normalizes the user's raw message (strips wake words, politeness,
       punctuation).
    2. Detects an intent (open_app / open_folder / open_file /
       open_website / unknown).
    3. Extracts a target (a canonical alias key, a raw file path, or a URL).

It NEVER touches the filesystem, launches a process, or opens a browser.
All actual OS interaction lives in tools/app_launcher.py, tools/file_opener.py,
and tools/web_tools.py - this module only imports their *alias dictionaries*
(pure data) to decide what the user meant, and calling code (assistant.py)
is responsible for invoking the matching tool function.

No LLM is used here - this is intentionally a transparent, deterministic
parser for Phase 1.
"""

import re
from enum import Enum
from typing import Optional, Tuple

from pydantic import BaseModel, Field
from tools.app_launcher import APP_ALIASES, get_discovered_aliases
from tools.file_opener import FOLDER_ALIASES
from tools.web_tools import SITE_SHORTCUTS


class Intent(str, Enum):
    OPEN_APP = "open_app"
    OPEN_FOLDER = "open_folder"
    OPEN_FILE = "open_file"
    OPEN_WEBSITE = "open_website"
    UNKNOWN = "unknown"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's raw text command.")


class ChatResponse(BaseModel):
    intent: Intent
    success: bool
    reply: str
    detail: Optional[str] = None


# --- Normalization patterns -------------------------------------------------

# Wake words: "jarvis", "hey jarvis", "hi jarvis", "ok jarvis", followed by
# optional punctuation, e.g. "Jarvis," / "Hey Jarvis:" / "Jarvis -"
_WAKE_WORD_RE = re.compile(r"^\s*(hey|hi|ok|okay)?\s*jarvis\s*[,:\-]?\s*", re.IGNORECASE)

# Politeness prefixes, e.g. "please", "can you", "could you", "would you"
_POLITE_RE = re.compile(r"^\s*(please|can you|could you|would you)\s+", re.IGNORECASE)

# The command verb: open / launch / start, followed by the target text.
_VERB_RE = re.compile(r"^\s*(open|launch|start)\s+(.+)$", re.IGNORECASE)

# Explicit keyword forms, kept for backwards compatibility and precision.
_APP_KEYWORD_RE = re.compile(r"^\s*app\s+(.+)$", re.IGNORECASE)
_FILE_KEYWORD_RE = re.compile(r"^\s*file\s+(.+)$", re.IGNORECASE)
_FOLDER_KEYWORD_RE = re.compile(r"^\s*folder\s+(.+)$", re.IGNORECASE)
_WEBSITE_KEYWORD_RE = re.compile(r"^\s*(?:website|site)\s+(.+)$", re.IGNORECASE)

# Raw path / URL detection.
_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_WINDOWS_PATH_RE = re.compile(r"^[a-zA-Z]:[\\/]")
_UNIX_PATH_RE = re.compile(r"^/[^\s]+")
_HAS_PATH_SEPARATOR_RE = re.compile(r"[\\/]")

# Filler words stripped when matching folder/app/site aliases,
# e.g. "my Downloads folder" -> "downloads".
_LEADING_FILLER_RE = re.compile(r"^\s*(my|the)\s+", re.IGNORECASE)
_TRAILING_FOLDER_RE = re.compile(r"\s+folder\s*$", re.IGNORECASE)

# File Explorer specific patterns - MUST be checked before generic folder handling
_FILE_EXPLORER_ALIASES = {
    "file explorer",
    "explorer",
    "windows explorer",
    "open file explorer",
    "open explorer",
    "open windows explorer",
}

# LeetCode specific patterns
_LEETCODE_WEBSITE_ALIASES = {
    "leetcode",
    "leetcode website",
    "leetcode web",
    "leetcode site",
}
_LEETCODE_DESKTOP_ALIASES = {
    "leetcode desktop",
    "leetcode app",
    "leetcode application",
}

# Spotify specific patterns (like LeetCode)
_SPOTIFY_WEBSITE_ALIASES = {
    "spotify",
    "spotify web",
    "spotify website",
    "spotify web player",
}
_SPOTIFY_DESKTOP_ALIASES = {
    "spotify desktop",
    "spotify app",
    "spotify application",
}


def _strip_prefixes(message: str) -> str:
    """Remove wake words and politeness phrasing, in any order, repeatedly."""
    text = message.strip()
    for _ in range(3):
        previous = text
        text = _WAKE_WORD_RE.sub("", text).strip()
        text = _POLITE_RE.sub("", text).strip()
        if text == previous:
            break
    return text


def _clean_alias_key(raw_target: str) -> str:
    """Normalize free text down to a bare alias key, e.g. 'my Downloads folder' -> 'downloads'."""
    key = raw_target.strip().lower()
    key = _LEADING_FILLER_RE.sub("", key)
    key = _TRAILING_FOLDER_RE.sub("", key)
    key = key.strip().rstrip("?!.").strip()
    return key


def _get_all_app_aliases() -> dict:
    """Get combined app aliases from whitelist and discovered apps."""
    aliases = dict(APP_ALIASES)
    aliases.update(get_discovered_aliases())
    return aliases


def parse_intent(message: str) -> Tuple[Intent, Optional[str]]:
    """
    Parse a raw, natural-language user message into an (Intent, target) pair.

    `target` meaning depends on the intent:
        OPEN_APP     -> canonical key into tools.app_launcher.APP_WHITELIST or discovered apps
        OPEN_FOLDER  -> canonical key into tools.file_opener.FOLDER_DISPLAY,
                        OR a raw folder path (explicit "folder <path>" form)
        OPEN_FILE    -> a raw file path
        OPEN_WEBSITE -> a raw URL, bare domain, or a key in SITE_SHORTCUTS
        UNKNOWN      -> None

    Supported phrasing (case-insensitive), after optional wake-word /
    politeness prefixes are stripped:
        "open app <name>"              (explicit form)
        "open website <name-or-url>"   (explicit form)
        "open folder <path>"           explicit filesystem path
        "open file <path>"
        "open <app name>"              e.g. "open VS Code", "launch spotify"
        "open <known folder>"          e.g. "open Downloads", "open my Documents folder"
        "open <url>"                   e.g. "open https://example.com"
        "open <known website name>"    e.g. "open youtube", "open google"
        "open <domain>"                e.g. "open python.org", "open example.com"
    """
    cleaned = _strip_prefixes(message)

    verb_match = _VERB_RE.match(cleaned)
    if not verb_match:
        return Intent.UNKNOWN, None

    target_raw = verb_match.group(2).strip().rstrip("?!.").strip()
    if not target_raw:
        return Intent.UNKNOWN, None

    # --- Explicit keyword forms (highest precedence, most specific) --------
    app_kw = _APP_KEYWORD_RE.match(target_raw)
    if app_kw:
        alias_key = _clean_alias_key(app_kw.group(1))
        all_app_aliases = _get_all_app_aliases()
        if alias_key in all_app_aliases:
            return Intent.OPEN_APP, all_app_aliases[alias_key]
        return Intent.UNKNOWN, None

    folder_kw = _FOLDER_KEYWORD_RE.match(target_raw)
    if folder_kw:
        remainder = folder_kw.group(1).strip()
        # "open folder /tmp" / "open folder C:\Users\me" -> explicit path
        if _HAS_PATH_SEPARATOR_RE.search(remainder):
            return Intent.OPEN_FOLDER, remainder
        # "open folder downloads" -> alias
        alias_key = _clean_alias_key(remainder)
        if alias_key in FOLDER_ALIASES:
            return Intent.OPEN_FOLDER, FOLDER_ALIASES[alias_key]
        return Intent.OPEN_FOLDER, remainder  # let the tool report "not found"

    website_kw = _WEBSITE_KEYWORD_RE.match(target_raw)
    if website_kw:
        return Intent.OPEN_WEBSITE, website_kw.group(1).strip()

    # --- Natural language: clean the target for alias matching ---------------
    alias_key = _clean_alias_key(target_raw)

    # --- 1. File Explorer (MUST be before generic "file" keyword) -----------
    if alias_key in _FILE_EXPLORER_ALIASES:
        return Intent.OPEN_APP, "explorer"

    # --- 2. LeetCode special handling ---------------------------------------
    if alias_key in _LEETCODE_WEBSITE_ALIASES:
        return Intent.OPEN_WEBSITE, "leetcode"

    if alias_key in _LEETCODE_DESKTOP_ALIASES:
        return Intent.OPEN_APP, "leetcode desktop"

    # --- 3. Spotify special handling (like LeetCode) ------------------------
    if alias_key in _SPOTIFY_WEBSITE_ALIASES:
        return Intent.OPEN_WEBSITE, "spotify"

    if alias_key in _SPOTIFY_DESKTOP_ALIASES:
        return Intent.OPEN_APP, "spotify"

    # --- 4. Known folder aliases --------------------------------------------
    if alias_key in FOLDER_ALIASES:
        return Intent.OPEN_FOLDER, FOLDER_ALIASES[alias_key]

    # --- 5. Known website aliases (before app aliases for known shortcuts) --
    if alias_key in SITE_SHORTCUTS:
        return Intent.OPEN_WEBSITE, alias_key

    # --- 6. App aliases (whitelist + discovered) ----------------------------
    all_app_aliases = _get_all_app_aliases()
    if alias_key in all_app_aliases:
        return Intent.OPEN_APP, all_app_aliases[alias_key]

    # --- 7. Explicit "file" keyword (after File Explorer check) -------------
    file_kw = _FILE_KEYWORD_RE.match(target_raw)
    if file_kw:
        return Intent.OPEN_FILE, file_kw.group(1).strip()

    # --- 6. Raw URL / raw file path (no keyword needed) ---------------------
    if _URL_RE.match(target_raw):
        return Intent.OPEN_WEBSITE, target_raw

    if _WINDOWS_PATH_RE.match(target_raw) or _UNIX_PATH_RE.match(target_raw):
        return Intent.OPEN_FILE, target_raw

    # --- 7. Bare domain detection (e.g. "python.org", "example.com") --------
    # If it looks like a domain (contains a dot, no spaces), treat as website
    if "." in alias_key and " " not in alias_key and not alias_key.startswith("."):
        # Additional validation: must look like a valid domain
        if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", alias_key):
            return Intent.OPEN_WEBSITE, target_raw

    return Intent.UNKNOWN, None