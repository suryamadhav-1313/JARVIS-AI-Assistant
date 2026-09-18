"""
test_router.py
---------------
Pure unit tests for core.router.parse_intent(). These tests never touch the
filesystem, launch a process, or open a browser - parse_intent() is a pure
text -> (Intent, target) function, so it can be tested directly and fast.
"""

import pytest

from core.router import Intent, parse_intent


# --- Websites: Known Aliases ---------------------------------------------------

@pytest.mark.parametrize(
    "phrase,expected_target",
    [
        ("open chatgpt", "chatgpt"),
        ("open claude", "claude"),
        ("open youtube", "youtube"),
        ("open google", "google"),
        ("open spotify", "spotify"),
        ("open leetcode", "leetcode"),
        ("open github", "github"),
        ("open gmail", "gmail"),
        ("open instagram", "instagram"),
        ("open linkedin", "linkedin"),
        ("open wikipedia", "wikipedia"),
        ("open facebook", "facebook"),
        ("open twitter", "twitter"),
        ("open x", "x"),
        ("open reddit", "reddit"),
        ("open stackoverflow", "stackoverflow"),
        ("open netflix", "netflix"),
        ("open amazon", "amazon"),
        ("open amazon.in", "amazon.in"),
        ("open flipkart", "flipkart"),
        ("open microsoft", "microsoft"),
        ("open python.org", "python.org"),
        ("open example.com", "example.com"),
    ],
)
def test_known_website_aliases(phrase, expected_target):
    intent, target = parse_intent(phrase)
    assert intent == Intent.OPEN_WEBSITE
    assert target == expected_target


# --- Websites: Arbitrary Domains/URLs -----------------------------------------

@pytest.mark.parametrize(
    "phrase,expected_target",
    [
        ("open python.org", "python.org"),
        ("open microsoft.com", "microsoft.com"),
        ("open wikipedia.org", "wikipedia.org"),
        ("open reddit.com", "reddit.com"),
        ("open stackoverflow.com", "stackoverflow.com"),
        ("open espn.com", "espn.com"),
        ("open netflix.com", "netflix.com"),
        ("open amazon.in", "amazon.in"),
        ("open flipkart.com", "flipkart.com"),
        ("open example.com", "example.com"),
        ("open https://example.com", "https://example.com"),
        ("open http://example.com", "http://example.com"),
        ("open www.example.com", "www.example.com"),
        ("open www.python.org", "www.python.org"),
        ("open https://python.org", "https://python.org"),
    ],
)
def test_arbitrary_website_domains(phrase, expected_target):
    intent, target = parse_intent(phrase)
    assert intent == Intent.OPEN_WEBSITE
    assert target == expected_target


# --- Websites: Dangerous Scheme Rejection -------------------------------------

@pytest.mark.parametrize(
    "phrase",
    [
        "open file:///C:/Users/test.txt",
        "open javascript:alert(1)",
        "open data:text/html,test",
        "open vbscript:test",
        "open about:blank",
        "open blob:test",
        "open filesystem:test",
    ],
)
def test_dangerous_url_schemes_rejected(phrase):
    intent, target = parse_intent(phrase)
    assert intent == Intent.UNKNOWN
    assert target is None


# --- Applications: Known Aliases ----------------------------------------------

@pytest.mark.parametrize(
    "phrase,expected_target",
    [
        ("open chrome", "chrome"),
        ("open google chrome", "chrome"),
        ("open chrome browser", "chrome"),
        ("open edge", "edge"),
        ("open microsoft edge", "edge"),
        ("open firefox", "firefox"),
        ("open mozilla firefox", "firefox"),
        ("open vscode", "vscode"),
        ("open visual studio code", "vscode"),
        ("open vs code", "vscode"),
        ("open code", "vscode"),
        ("open notepad", "notepad"),
        ("open calculator", "calculator"),
        ("open calc", "calculator"),
        ("open discord", "discord"),
        ("open spotify app", "spotify"),
        ("open steam", "steam"),
        ("open epic games", "epic games"),
        ("open epic games launcher", "epic games"),
        ("open slack", "slack"),
        ("open teams", "teams"),
        ("open microsoft teams", "teams"),
        ("open zoom", "zoom"),
        ("open outlook", "outlook"),
        ("open word", "word"),
        ("open excel", "excel"),
        ("open powerpoint", "powerpoint"),
        ("open onenote", "onenote"),
        ("open brave", "brave"),
        ("open opera", "opera"),
        ("open vivaldi", "vivaldi"),
    ],
)
def test_app_aliases(phrase, expected_target):
    intent, target = parse_intent(phrase)
    assert intent == Intent.OPEN_APP
    assert target == expected_target


# --- Applications: Games ------------------------------------------------------

@pytest.mark.parametrize(
    "phrase,expected_target",
    [
        ("open minecraft", "minecraft"),
        ("open valorant", "valorant"),
        ("open gta", "gta"),
        ("open gta v", "gta"),
        ("open roblox", "roblox"),
        ("open league of legends", "league of legends"),
        ("open overwatch", "overwatch"),
        ("open battle.net", "battle.net"),
        ("open blizzard", "battle.net"),
    ],
)
def test_game_aliases(phrase, expected_target):
    intent, target = parse_intent(phrase)
    assert intent == Intent.OPEN_APP
    assert target == expected_target


# --- File Explorer ------------------------------------------------------------

@pytest.mark.parametrize(
    "phrase",
    [
        "open file explorer",
        "open explorer",
        "open windows explorer",
        "OPEN FILE EXPLORER",
        "Open Explorer",
        "Hey Jarvis, open file explorer",
    ],
)
def test_file_explorer_aliases(phrase):
    intent, target = parse_intent(phrase)
    assert intent == Intent.OPEN_APP
    assert target == "explorer"


# --- LeetCode Handling --------------------------------------------------------

def test_open_leetcode_website():
    intent, target = parse_intent("open leetcode")
    assert intent == Intent.OPEN_WEBSITE
    assert target == "leetcode"


def test_open_leetcode_website_explicit():
    intent, target = parse_intent("open leetcode website")
    assert intent == Intent.OPEN_WEBSITE
    assert target == "leetcode"


def test_open_leetcode_web():
    intent, target = parse_intent("open leetcode web")
    assert intent == Intent.OPEN_WEBSITE
    assert target == "leetcode"


def test_open_leetcode_desktop():
    intent, target = parse_intent("open leetcode desktop")
    assert intent == Intent.OPEN_APP
    assert target == "leetcode desktop"


def test_open_leetcode_app():
    intent, target = parse_intent("open leetcode app")
    assert intent == Intent.OPEN_APP
    assert target == "leetcode desktop"


def test_open_leetcode_application():
    intent, target = parse_intent("open leetcode application")
    assert intent == Intent.OPEN_APP
    assert target == "leetcode desktop"


# --- Explicit Keyword Forms ---------------------------------------------------

def test_open_app_explicit_keyword():
    intent, target = parse_intent("open app notepad")
    assert intent == Intent.OPEN_APP
    assert target == "notepad"


def test_open_website_explicit_keyword():
    intent, target = parse_intent("open website youtube")
    assert intent == Intent.OPEN_WEBSITE
    assert target == "youtube"


def test_open_website_explicit_keyword_with_domain():
    intent, target = parse_intent("open website python.org")
    assert intent == Intent.OPEN_WEBSITE
    assert target == "python.org"


# --- Case Insensitivity for New Commands -------------------------------------

@pytest.mark.parametrize(
    "phrase,expected_intent,expected_target",
    [
        ("OPEN CHATGPT", Intent.OPEN_WEBSITE, "chatgpt"),
        ("Open Chrome", Intent.OPEN_APP, "chrome"),
        ("OPEN FILE EXPLORER", Intent.OPEN_APP, "explorer"),
        ("Open LeetCode", Intent.OPEN_WEBSITE, "leetcode"),
        ("OPEN LEETCODE DESKTOP", Intent.OPEN_APP, "leetcode desktop"),
    ],
)
def test_case_insensitivity_new_commands(phrase, expected_intent, expected_target):
    intent, target = parse_intent(phrase)
    assert intent == expected_intent
    assert target == expected_target


# --- Priority Ordering --------------------------------------------------------

def test_file_explorer_before_generic_folder():
    """
    'open file explorer' must be recognized as the File Explorer app,
    not as a generic folder command.
    """
    intent, target = parse_intent("open file explorer")
    assert intent == Intent.OPEN_APP
    assert target == "explorer"


def test_app_before_website():
    """
    Known app aliases (like 'discord') must be recognized as apps
    before being treated as potential website domains.
    """
    intent, target = parse_intent("open discord")
    assert intent == Intent.OPEN_APP
    assert target == "discord"


def test_website_before_generic_domain():
    """
    Known website aliases (like 'youtube') must be recognized as websites
    before being treated as potential app names.
    """
    intent, target = parse_intent("open youtube")
    assert intent == Intent.OPEN_WEBSITE
    assert target == "youtube"


# --- Folders ------------------------------------------------------------------

def test_open_downloads():
    intent, target = parse_intent("open Downloads")
    assert intent == Intent.OPEN_FOLDER
    assert target == "downloads"


def test_open_my_downloads_folder_phrase():
    intent, target = parse_intent("open my Downloads folder")
    assert intent == Intent.OPEN_FOLDER
    assert target == "downloads"


def test_open_documents():
    intent, target = parse_intent("open Documents")
    assert intent == Intent.OPEN_FOLDER
    assert target == "documents"


def test_open_my_documents_folder_phrase():
    intent, target = parse_intent("open my Documents folder")
    assert intent == Intent.OPEN_FOLDER
    assert target == "documents"


def test_open_folder_explicit_path_backwards_compat():
    intent, target = parse_intent("open folder /tmp")
    assert intent == Intent.OPEN_FOLDER
    assert target == "/tmp"


# --- Files --------------------------------------------------------------------

def test_open_file_explicit_windows_path():
    intent, target = parse_intent(r"open file C:\Users\ASUS\Documents\resume.pdf")
    assert intent == Intent.OPEN_FILE
    assert target == r"C:\Users\ASUS\Documents\resume.pdf"


def test_open_file_raw_windows_path_no_keyword():
    intent, target = parse_intent(r"open C:\Users\ASUS\Documents\resume.pdf")
    assert intent == Intent.OPEN_FILE
    assert target == r"C:\Users\ASUS\Documents\resume.pdf"


# --- Case-insensitivity -------------------------------------------------------

def test_case_insensitivity_all_caps():
    intent, target = parse_intent("HEY JARVIS, OPEN YOUTUBE")
    assert intent == Intent.OPEN_WEBSITE
    assert target == "youtube"


def test_case_insensitivity_mixed_case():
    intent, target = parse_intent("OpEn YouTube")
    assert intent == Intent.OPEN_WEBSITE
    assert target == "youtube"


# --- Wake word / politeness prefixes ------------------------------------------

@pytest.mark.parametrize(
    "phrase",
    [
        "Jarvis, open YouTube",
        "Hey Jarvis, open YouTube",
        "hey jarvis open youtube",
        "Please open YouTube",
        "Can you open YouTube?",
        "Could you open YouTube",
        "Hey Jarvis, please open YouTube",
    ],
)
def test_prefix_stripping_all_resolve_the_same(phrase):
    intent, target = parse_intent(phrase)
    assert intent == Intent.OPEN_WEBSITE
    assert target == "youtube"


def test_can_you_open_spotify_with_question_mark():
    intent, target = parse_intent("Can you open Spotify?")
    assert intent == Intent.OPEN_WEBSITE
    assert target == "spotify"


# --- Invalid / unrecognized commands ------------------------------------------

def test_invalid_command_returns_unknown():
    intent, target = parse_intent("asdkjh qwoiuey random gibberish")
    assert intent == Intent.UNKNOWN
    assert target is None


def test_empty_message_after_verb_returns_unknown():
    intent, target = parse_intent("open")
    assert intent == Intent.UNKNOWN
    assert target is None


def test_unrecognized_app_name_returns_unknown():
    intent, target = parse_intent("open photoshop")
    assert intent == Intent.UNKNOWN
    assert target is None


# --- Arbitrary shell command rejection ----------------------------------------

@pytest.mark.parametrize(
    "phrase",
    [
        "open app; rm -rf /",
        "open cmd.exe && del *.*",
        "open notepad & shutdown -s -t 0",
        "run rm -rf /",
        "delete all my files",
        "open $(rm -rf /)",
    ],
)
def test_arbitrary_shell_commands_are_never_matched_to_a_safe_action(phrase):
    """
    None of these should resolve to a recognized app/folder/file/website
    target. Either there's no open/launch/start verb at all ("run ...",
    "delete ..."), or the text after the verb doesn't match any alias in
    APP_ALIASES / FOLDER_ALIASES / SITE_SHORTCUTS, and it isn't a raw
    path or URL either - so parse_intent must return UNKNOWN rather than
    inventing a target string that some other layer might later execute.
    """
    intent, target = parse_intent(phrase)
    assert intent == Intent.UNKNOWN
    assert target is None