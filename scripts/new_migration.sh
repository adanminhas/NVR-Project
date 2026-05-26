#!/usr/bin/env bash
# Generate a new Alembic migration with an --autogenerate diff against models.
# Usage: ./scripts/new_migration.sh "short description"
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 \"short description\"" >&2
  exit 1
fi

cd "$(dirname "$0")/../backend"
exec ./venv/bin/alembic revision --autogenerate -m "$1"
