"""
Application configuration using Pydantic Settings.

Defines environment-based settings for the API runtime.
"""

import sys
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Defines configuration values for the API runtime and environment setup.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "FastAPI Boilerplate API"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    api_prefix: str = "/api/v1"
    python_version: str = "3.13"

    # Server
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Enable auto-reload")

    # Database
    database_url: str = Field(
        default="sqlite:///./data/app.db",
        description="Database connection URL",
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # CORS - stored as comma-separated string, converted to list via property
    cors_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://localhost:5173",
        description="Allowed CORS origins (comma-separated)",
        alias="cors_origins",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins as a list."""
        if not str(self.cors_origins_str).strip():
            return []  # pragma: no cover
        return [
            origin.strip() for origin in str(self.cors_origins_str).split(",") if origin.strip()
        ]

    # PyInstaller support
    @property
    def database_path(self) -> Path:
        """Get database path, handling PyInstaller bundled paths."""
        if getattr(self, "_frozen", False):
            # Running from PyInstaller bundle

            if hasattr(sys, "_MEIPASS"):
                # PyInstaller temporary folder
                base_path = Path(sys.executable).parent
            else:
                base_path = Path.cwd()
        else:
            # Normal execution
            base_path = Path.cwd()

        db_path = base_path / "data" / "app.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path

    @property
    def resolved_database_url(self) -> str:
        """Get resolved database URL with proper path."""
        if str(self.database_url).startswith("sqlite:///"):
            return f"sqlite:///{str(self.database_path)}"
        return self.database_url


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


settings = get_settings()
