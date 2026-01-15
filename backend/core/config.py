from typing import List, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator

# Get the backend directory (parent of core folder)
BACKEND_DIR = Path(__file__).parent.parent.resolve()  # Use resolve() to get absolute path

# Game configuration constants (module-level, not part of Settings)
PREMIER_LEAGUE_NAME = "Premier League"  # League name as stored in database
PREMIER_LEAGUE_API_ID = 39  # API-Football league ID for Premier League
MAX_GUESSES = 6  # Maximum number of guesses per game

class Settings(BaseSettings):
    # Use absolute path to ensure all scripts use the same database
    # Database will be in the backend directory
    # Convert Path to string and use forward slashes for SQLite compatibility
    DATABASE_URL: str = f"sqlite:///{(BACKEND_DIR / 'soccer_wordle.db').as_posix()}"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    API_PREFIX: str = "/api/"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    soccer_api_key: Optional[str] = None  # Optional API key for external soccer API

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            return ",".join(v)
        return "http://localhost:5173, https://plguesser.vercel.app, https://pl-guesser.vercel.app"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated string to list"""
        origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        # Ensure local dev origins are always allowed
        for default_origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
            if default_origin not in origins:
                origins.append(default_origin)
        return origins

    class Config:
        env_file = str(BACKEND_DIR / ".env")  # Look for .env in backend directory
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file that aren't defined here

settings = Settings()
