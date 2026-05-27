#!/usr/bin/env bash
# Start the frontend Vite dev server.
# Bind to 0.0.0.0 so other devices on the LAN (e.g. your phone) can connect.
set -euo pipefail

cd "$(dirname "$0")/../frontend"
exec npm run dev -- --host 0.0.0.0
