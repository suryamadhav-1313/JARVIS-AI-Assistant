"""
assistant.py
------------
The Assistant class ties the router (intent parsing) to the individual
tools. This is the single place that decides "given this parsed intent
and target, which tool function do I call, and how do I phrase the
reply?".

No AI model call happens here yet - this phase is purely rule-based so
the whole request/response path can be tested end-to-end before any
model is introduced.
"""
from core.router import ChatResponse, Intent, parse_intent
from tools.app_launcher import AppLaunchError, open_app
from tools.file_opener import FileOpenError, open_file, open_folder, open_known_folder
from tools.web_tools import WebOpenError, open_website


class Assistant:
    def handle_message(self, message: str) -> ChatResponse:
        intent, target = parse_intent(message)

        if intent == Intent.UNKNOWN or not target:
            return ChatResponse(
                intent=Intent.UNKNOWN,
                success=False,
                reply=(
                    "I didn't understand that command. Try things like "
                    "'open YouTube', 'open VS Code', 'open Downloads', "
                    "'open file C:\\path\\to\\file.pdf', or 'open https://example.com'."
                ),
            )

        try:
            if intent == Intent.OPEN_APP:
                result = open_app(target)
                reply = f"Opening {result['display']}."
                detail = result["display"]

            elif intent == Intent.OPEN_FOLDER:
                # `target` is either a canonical known-folder key (e.g. "downloads")
                # or an explicit path (from "open folder <path>").
                if target in ("downloads", "documents", "desktop", "pictures", "videos", "music"):
                    result = open_known_folder(target)
                else:
                    result = open_folder(target)
                reply = f"Opening {result['display']}."
                detail = result["path"]

            elif intent == Intent.OPEN_FILE:
                result = open_file(target)
                reply = f"Opening {result['display']}."
                detail = result["path"]

            elif intent == Intent.OPEN_WEBSITE:
                result = open_website(target)
                reply = f"Opening {result['display']}."
                detail = result["url"]

            else:
                # Should be unreachable given the checks above.
                raise ValueError(f"Unhandled intent: {intent}")

            return ChatResponse(intent=intent, success=True, reply=reply, detail=detail)

        except (AppLaunchError, FileOpenError, WebOpenError) as exc:
            return ChatResponse(
                intent=intent,
                success=False,
                reply="I couldn't complete that action.",
                detail=str(exc),
            )


# Shared singleton instance used by the API layer.
assistant = Assistant()
