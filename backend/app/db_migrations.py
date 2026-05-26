"""
Lightweight startup migrations.

Stage 7 will introduce proper Alembic migrations. Until then, this module runs
on backend startup to bring existing databases in line with the current models
(e.g. adding new columns).
"""

from sqlalchemy import inspect, text

from app.database import Base, engine
from app.models import camera_model  # noqa: F401 — register tables
from app.models import recording_model  # noqa: F401 — register tables
from app.models import user_model  # noqa: F401 — register tables


def _column_exists(table: str, column: str) -> bool:
    inspector = inspect(engine)
    return column in {col["name"] for col in inspector.get_columns(table)}


def _ensure_camera_recording_mode_column() -> None:
    if not _column_exists("cameras", "recording_mode"):
        with engine.connect() as conn:
            conn.execute(
                text(
                    "ALTER TABLE cameras "
                    "ADD COLUMN recording_mode VARCHAR(20) NOT NULL DEFAULT 'off'"
                )
            )
            conn.commit()


def run_migrations() -> None:
    """Create any missing tables and apply ad-hoc column additions."""
    Base.metadata.create_all(bind=engine)
    _ensure_camera_recording_mode_column()
