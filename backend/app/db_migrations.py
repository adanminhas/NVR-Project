"""
Alembic-driven migrations for the backend.

On startup we either:
  - `alembic stamp head` — if the project's tables already exist but the
    `alembic_version` table is missing (pre-Alembic install), mark the DB
    as being at the current head without running any DDL.
  - `alembic upgrade head` — otherwise (fresh install or behind on
    migrations), apply pending revisions in order.

To create a new migration after changing models:
    cd backend
    ./venv/bin/alembic revision --autogenerate -m "describe change"
    ./venv/bin/alembic upgrade head
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.database import engine


BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
ALEMBIC_INI = BASE_DIR / "alembic.ini"


def _alembic_config() -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", str(BASE_DIR / "alembic"))
    return cfg


def _has_existing_pre_alembic_schema() -> bool:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    return "cameras" in tables and "alembic_version" not in tables


def run_migrations() -> None:
    cfg = _alembic_config()
    if _has_existing_pre_alembic_schema():
        # Adopt the existing schema as the baseline without touching DDL.
        command.stamp(cfg, "head")
    else:
        command.upgrade(cfg, "head")
