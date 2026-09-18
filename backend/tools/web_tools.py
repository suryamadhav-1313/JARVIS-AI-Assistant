"""
web_tools.py
------------

Opens websites directly in Google Chrome.

Safety rules:
- Only http/https URLs are ever opened.
- No shell commands are constructed.
- Known website shortcuts such as "youtube" are supported.
- Arbitrary valid domains are also supported.
- Dangerous URL schemes are rejected.
- Google Chrome is launched directly instead of using the Windows
  default browser, so Microsoft Edge will not be used.
"""

import os
import re
import subprocess
import webbrowser
from typing import Dict, Optional
from urllib.parse import urlparse


# -------------------------------------------------------------------
# Friendly website shortcuts
# -------------------------------------------------------------------

SITE_SHORTCUTS: Dict[str, Dict[str, str]] = {
    "chatgpt": {
        "url": "https://chatgpt.com",
        "display": "ChatGPT",
    },
    "claude": {
        "url": "https://claude.ai",
        "display": "Claude",
    },
    "youtube": {
        "url": "https://www.youtube.com",
        "display": "YouTube",
    },
    "google": {
        "url": "https://www.google.com",
        "display": "Google",
    },
    "spotify": {
        "url": "https://open.spotify.com",
        "display": "Spotify Web",
    },
    "leetcode": {
        "url": "https://leetcode.com",
        "display": "LeetCode",
    },
    "github": {
        "url": "https://github.com",
        "display": "GitHub",
    },
    "gmail": {
        "url": "https://mail.google.com",
        "display": "Gmail",
    },
    "instagram": {
        "url": "https://www.instagram.com",
        "display": "Instagram",
    },
    "linkedin": {
        "url": "https://www.linkedin.com",
        "display": "LinkedIn",
    },
    "wikipedia": {
        "url": "https://www.wikipedia.org",
        "display": "Wikipedia",
    },
    "facebook": {
        "url": "https://www.facebook.com",
        "display": "Facebook",
    },
    "twitter": {
        "url": "https://www.twitter.com",
        "display": "Twitter / X",
    },
    "x": {
        "url": "https://www.twitter.com",
        "display": "Twitter / X",
    },
    "reddit": {
        "url": "https://www.reddit.com",
        "display": "Reddit",
    },
    "stackoverflow": {
        "url": "https://stackoverflow.com",
        "display": "Stack Overflow",
    },
    "netflix": {
        "url": "https://www.netflix.com",
        "display": "Netflix",
    },
    "amazon": {
        "url": "https://www.amazon.com",
        "display": "Amazon",
    },
    "amazon.in": {
        "url": "https://www.amazon.in",
        "display": "Amazon India",
    },
    "flipkart": {
        "url": "https://www.flipkart.com",
        "display": "Flipkart",
    },
    "microsoft": {
        "url": "https://www.microsoft.com",
        "display": "Microsoft",
    },
    "python.org": {
        "url": "https://python.org",
        "display": "Python.org",
    },
    "example.com": {
        "url": "https://example.com",
        "display": "Example.com",
    },
}


# -------------------------------------------------------------------
# Security / validation
# -------------------------------------------------------------------

_DANGEROUS_SCHEMES = {
    "file",
    "javascript",
    "data",
    "vbscript",
    "about",
    "blob",
    "filesystem",
    "ws",
    "wss",
}


_DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9-]+\.)+"
    r"[a-zA-Z]{2,}"
    r"(?:[/?#][^\s]*)?$"
)


class WebOpenError(Exception):
    """Raised when a website cannot safely be opened."""

    pass


# -------------------------------------------------------------------
# Website shortcut handling
# -------------------------------------------------------------------

def resolve_site_alias(name: str) -> Optional[Dict[str, str]]:
    """
    Look up a website shortcut.

    Example:
        "youtube" -> {"url": "https://www.youtube.com", ...}

    Returns:
        Dictionary containing URL and display name, or None.
    """

    if not name:
        return None

    return SITE_SHORTCUTS.get(name.strip().lower())


# -------------------------------------------------------------------
# URL safety
# -------------------------------------------------------------------

def _is_dangerous_url(url: str) -> bool:
    """
    Return True if the URL uses a dangerous scheme.
    """

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()

    return scheme in _DANGEROUS_SCHEMES


def _normalize_url(raw: str) -> str:
    """
    Convert a user-provided domain into a full HTTPS URL.

    Examples:

        youtube.com
        -> https://youtube.com

        www.youtube.com
        -> https://www.youtube.com

        https://youtube.com
        -> https://youtube.com
    """

    raw = raw.strip()
    lower = raw.lower()

    if lower.startswith(("http://", "https://")):
        return raw

    if lower.startswith("www."):
        return f"https://{raw}"

    return f"https://{raw}"


def _is_valid_domain_or_url(raw: str) -> bool:
    """
    Perform basic validation to ensure the input looks like
    a valid website address.
    """

    raw = raw.strip().lower()

    # Full HTTP/HTTPS URL
    if raw.startswith(("http://", "https://")):
        parsed = urlparse(raw)

        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
        )

    # www.example.com
    if raw.startswith("www."):
        return bool(_DOMAIN_RE.match(raw))

    # example.com
    return bool(_DOMAIN_RE.match(raw))


# -------------------------------------------------------------------
# Resolve website
# -------------------------------------------------------------------

def _resolve(url_or_name: str) -> Dict[str, str]:
    """
    Resolve a user input into a safe website URL.

    Resolution order:

    1. Check known shortcuts.
    2. Otherwise treat input as a URL/domain.
    3. Normalize to HTTPS.
    4. Validate the final URL.
    """

    raw = url_or_name.strip()

    # Check shortcuts first
    shortcut = resolve_site_alias(raw)

    if shortcut:
        return dict(shortcut)

    # Validate user-provided domain/URL
    if not _is_valid_domain_or_url(raw):
        raise WebOpenError(
            f"'{url_or_name}' is not a valid website address."
        )

    # Normalize
    normalized = _normalize_url(raw)

    # Security check
    if _is_dangerous_url(normalized):
        raise WebOpenError(
            f"'{url_or_name}' uses a blocked URL scheme."
        )

    # Final validation
    parsed = urlparse(normalized)

    if parsed.scheme not in ("http", "https"):
        raise WebOpenError(
            f"'{url_or_name}' is not a valid HTTP/HTTPS URL."
        )

    if not parsed.netloc:
        raise WebOpenError(
            f"'{url_or_name}' is not a valid website address."
        )

    return {
        "url": normalized,
        "display": raw,
    }


# -------------------------------------------------------------------
# Find Google Chrome
# -------------------------------------------------------------------

def _find_chrome() -> Optional[str]:
    """
    Find Google Chrome on Windows.

    Checks the most common Chrome installation locations.
    """

    chrome_paths = [
        # Standard 64-bit installation
        os.path.join(
            os.environ.get("PROGRAMFILES", ""),
            "Google",
            "Chrome",
            "Application",
            "chrome.exe",
        ),

        # 32-bit Chrome on 64-bit Windows
        os.path.join(
            os.environ.get("PROGRAMFILES(X86)", ""),
            "Google",
            "Chrome",
            "Application",
            "chrome.exe",
        ),

        # Chrome installed for the current Windows user
        os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Google",
            "Chrome",
            "Application",
            "chrome.exe",
        ),
    ]

    for path in chrome_paths:
        if path and os.path.exists(path):
            return path

    return None


# -------------------------------------------------------------------
# Open website
# -------------------------------------------------------------------

def open_website(url_or_name: str) -> dict:
    """
    Open a website directly in Google Chrome.

    Examples:

        open_website("youtube")

        open_website("google")

        open_website("https://leetcode.com")

        open_website("github.com")

    Returns:

        {
            "url": "...",
            "display": "..."
        }

    Raises:
        WebOpenError if the URL is invalid or Chrome cannot be found.
    """

    if not url_or_name or not url_or_name.strip():
        raise WebOpenError(
            "No URL or site name was provided."
        )

    # Resolve and validate the website
    resolved = _resolve(url_or_name)

    url = resolved["url"]

    # Find Chrome
    chrome_path = _find_chrome()

    if not chrome_path:
        raise WebOpenError(
            "Google Chrome was not found on this computer."
        )

    # Open URL directly with Chrome
    try:
        subprocess.Popen(
            [
                chrome_path,
                url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True,
        )

    except Exception as exc:
        raise WebOpenError(
            f"Could not open Google Chrome: {exc}"
        ) from exc

    return resolved