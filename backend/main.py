"""
main.py
-------
FastAPI entry point for the JARVIS backend (Phase 1).

Endpoints:
    GET  /health   - liveness/health check
    POST /chat     - send a text command, get back a structured response

Run with:
    uvicorn main:app --reload --host 127.0.0.1 --port 8000
(from inside the backend/ directory)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from core.assistant import assistant
from core.router import ChatRequest, ChatResponse

app = FastAPI(
    title=settings.app_name,
    description="JARVIS AI Assistant backend - Phase 1 foundation.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    """Simple liveness check so the frontend/UI can confirm the backend is up."""
    return HealthResponse(status="ok", app_name=settings.app_name, version=app.version)


@app.post("/chat", response_model=ChatResponse, tags=["assistant"])
def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a text command to JARVIS.

    Supported commands right now:
        "open app <name>"
        "open folder <path>"
        "open file <path>"
        "open website <url>"
    """
    return assistant.handle_message(request.message)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
