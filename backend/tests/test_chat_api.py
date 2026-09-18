"""
test_chat_api.py
------------------
End-to-end tests through the FastAPI /chat endpoint, covering the full
path: HTTP -> router.parse_intent -> assistant -> tools.

Real OS side effects (os.startfile, webbrowser.open, subprocess.Popen) are
monkeypatched so tests are safe to run on any machine/OS (including this
Linux sandbox) without actually launching apps, opening a browser, or
depending on Windows-only APIs.
"""

import platform

import pytest
from fastapi.testclient import TestClient

import tools.app_launcher as app_launcher
import tools.file_opener as file_opener
import tools.web_tools as web_tools
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def safe_os_calls(monkeypatch, tmp_path):
    """
    Prevent any test from actually launching a program, opening a real
    browser, or depending on a real Windows user profile.
    """
    # Never actually open a browser - just record the call and report success.
    opened_urls = []
    monkeypatch.setattr(web_tools.webbrowser, "open", lambda url: opened_urls.append(url) or True)

    # Never actually launch a process. `raising=False` because os.startfile
    # doesn't exist at all on non-Windows platforms.
    launched = []
    monkeypatch.setattr(
        app_launcher.os, "startfile", lambda target: launched.append(target), raising=False
    )
    monkeypatch.setattr(app_launcher.subprocess, "Popen", lambda args: launched.append(args))
    monkeypatch.setattr(app_launcher.platform, "system", lambda: "Windows")

    monkeypatch.setattr(
        file_opener.os, "startfile", lambda target: launched.append(target), raising=False
    )
    monkeypatch.setattr(file_opener.subprocess, "Popen", lambda args: launched.append(args))
    monkeypatch.setattr(file_opener.platform, "system", lambda: "Windows")

    # Point Path.home() at a fake, isolated "user profile" for folder tests.
    fake_home = tmp_path / "ASUS"
    for folder in ("Downloads", "Documents", "Desktop", "Pictures", "Videos", "Music"):
        (fake_home / folder).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(file_opener.Path, "home", classmethod(lambda cls: fake_home))

    yield {"opened_urls": opened_urls, "launched": launched, "fake_home": fake_home}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "JARVIS"


def test_chat_open_youtube_matches_spec_shape():
    response = client.post("/chat", json={"message": "open youtube"})
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "intent": "open_website",
        "success": True,
        "reply": "Opening YouTube.",
        "detail": "https://www.youtube.com",
    }


def test_chat_open_google():
    response = client.post("/chat", json={"message": "Open Google"})
    body = response.json()
    assert body["intent"] == "open_website"
    assert body["success"] is True
    assert body["detail"] == "https://www.google.com"


def test_chat_launch_spotify(safe_os_calls):
    response = client.post("/chat", json={"message": "launch spotify app"})
    body = response.json()
    assert body["intent"] == "open_app"
    assert body["success"] is True
    assert body["reply"] == "Opening Spotify."
    # The Spotify protocol handler should have been tried.
    assert "spotify:" in safe_os_calls["launched"]


def test_chat_open_vscode():
    response = client.post("/chat", json={"message": "open VS Code"})
    body = response.json()
    assert body["intent"] == "open_app"
    assert body["success"] is True
    assert body["reply"] == "Opening VS Code."


def test_chat_open_downloads_matches_spec_shape(safe_os_calls):
    response = client.post("/chat", json={"message": "open Downloads"})
    body = response.json()
    assert body["intent"] == "open_folder"
    assert body["success"] is True
    assert body["reply"] == "Opening Downloads."
    assert body["detail"] == str(safe_os_calls["fake_home"] / "Downloads")


def test_chat_open_documents_via_natural_phrase(safe_os_calls):
    response = client.post("/chat", json={"message": "open my Documents folder"})
    body = response.json()
    assert body["intent"] == "open_folder"
    assert body["success"] is True
    assert body["detail"] == str(safe_os_calls["fake_home"] / "Documents")


def test_chat_case_insensitivity():
    response = client.post("/chat", json={"message": "HEY JARVIS, OPEN YOUTUBE"})
    body = response.json()
    assert body["intent"] == "open_website"
    assert body["success"] is True


def test_chat_hey_jarvis_prefix():
    response = client.post("/chat", json={"message": "Hey Jarvis, open YouTube"})
    body = response.json()
    assert body["intent"] == "open_website"
    assert body["success"] is True
    assert body["reply"] == "Opening YouTube."


def test_chat_invalid_command():
    response = client.post("/chat", json={"message": "qwoiuey gibberish text"})
    body = response.json()
    assert body["intent"] == "unknown"
    assert body["success"] is False


@pytest.mark.parametrize(
    "phrase",
    [
        "open app; rm -rf /",
        "open cmd.exe && del *.*",
        "run rm -rf /",
        "delete all my files",
    ],
)
def test_chat_arbitrary_shell_commands_are_rejected(phrase, safe_os_calls):
    """
    None of these should launch anything. Either the router returns
    'unknown' outright, or - critically - nothing is ever passed to
    os.startfile / subprocess.Popen as a result of this input.
    """
    response = client.post("/chat", json={"message": phrase})
    body = response.json()
    assert body["success"] is False
    assert body["intent"] == "unknown"
    # Nothing should have been launched as a side effect of this request.
    assert safe_os_calls["launched"] == []
