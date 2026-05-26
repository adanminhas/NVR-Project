#!/usr/bin/env bash
# Run pending Alembic migrations against the configured DATABASE_URL.
set -euo pipefail

cd "$(dirname "$0")/../backend"
exec ./venv/bin/alembic upgrade head
