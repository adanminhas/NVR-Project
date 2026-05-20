from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    environment: str = "development"

    database_url: str = "sqlite:///./nvr.db"

    streams_dir: Path = BASE_DIR / "streams"

    # Comma-separated list of allowed origins. Use .cors_origins for the parsed list.
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    ffmpeg_path: str = "ffmpeg"
    hls_segment_seconds: int = 2
    hls_list_size: int = 5

    retention_days: int = 7

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
settings.streams_dir.mkdir(parents=True, exist_ok=True)
