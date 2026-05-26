#!/usr/bin/env bash
# Start the frontend Vite dev server.
set -euo pipefail

cd "$(dirname "$0")/../frontend"
exec npm run dev
