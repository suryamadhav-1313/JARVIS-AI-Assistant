"""
config.py
---------
Central configuration for the JARVIS backend.

Settings are loaded from environment variables (and a local `.env` file)
using pydantic-settings. Nothing in here executes commands or touches the
filesystem beyond reading configuration values.
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    app_name: str = "JARVIS"
    debug: bool = True

    # --- Server ---
    host: str = "127.0.0.1"
    port: int = 8000

    # --- CORS ---
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # --- Safety ---
    # Root folders JARVIS is allowed to open files/folders from.
    # Empty list = no restriction beyond "path must exist" (see file_opener.py).
    allowed_roots: List[str] = []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Single shared settings instance, imported elsewhere as `from config import settings`
settings = Settings()

# Base directory of the backend package (useful later for locating static assets, etc.)
BASE_DIR = Path(__file__).resolve().parent
