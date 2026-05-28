#!/usr/bin/env bash
#
# One-shot installer for a Raspberry Pi (or any Debian/Ubuntu host).
#
#   curl -O https://.../install_pi.sh   # or clone the repo and run from inside
#   bash scripts/install_pi.sh
#
# Installs system deps, sets up the backend venv, builds the frontend, writes
# a backend/.env with sane defaults and a random admin password, then registers
# and starts a systemd service that auto-starts on boot.
#
# Re-runnable: existing venv/.env/service are reused rather than overwritten.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE_USER="${SERVICE_USER:-$(whoami)}"
SERVICE_NAME="pi-nvr"
PORT="${PORT:-8000}"

log() { printf "\n\033[1;34m==>\033[0m %s\n" "$*"; }

if [ "$SERVICE_USER" = "root" ]; then
  echo "Refusing to run as root. Run as your normal user; sudo is invoked where needed." >&2
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This script targets Debian/Ubuntu/Raspberry Pi OS (apt). Aborting." >&2
  exit 1
fi

log "Installing Pi NVR from $PROJECT_DIR as user '$SERVICE_USER'"

# -------- 1. System packages --------------------------------------------------
log "Installing system packages (python, ffmpeg, avahi for .local mDNS, build tools)"
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
  python3 python3-venv python3-pip \
  ffmpeg \
  git curl \
  avahi-daemon \
  build-essential

# Node 20 LTS — install if missing or too old.
if ! command -v node >/dev/null 2>&1 \
  || [ "$(node -v | sed 's/v//;s/\..*//')" -lt 20 ]; then
  log "Installing Node 20 LTS via NodeSource"
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

# -------- 2. Backend ----------------------------------------------------------
log "Setting up backend venv"
cd "$PROJECT_DIR/backend"
if [ ! -d venv ]; then
  python3 -m venv venv
fi
./venv/bin/python -m pip install --upgrade pip --quiet
./venv/bin/python -m pip install -r requirements.txt --quiet

if [ ! -f .env ]; then
  log "Setting up backend/.env"

  # Admin credentials: prompt if interactive, allow env-var override,
  # fall back to a random password if neither is available (e.g. curl|bash).
  : "${ADMIN_USERNAME:=}"
  : "${ADMIN_PASSWORD:=}"

  if [ -t 0 ] && [ -z "$ADMIN_USERNAME" ]; then
    read -r -p "Admin username [admin]: " ADMIN_USERNAME
  fi
  ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"

  if [ -t 0 ] && [ -z "$ADMIN_PASSWORD" ]; then
    while true; do
      read -r -s -p "Admin password (min 4 chars, blank to auto-generate): " p1
      echo
      if [ -z "$p1" ]; then
        break
      fi
      if [ "${#p1}" -lt 4 ]; then
        echo "  Too short. At least 4 characters."
        continue
      fi
      read -r -s -p "Confirm password: " p2
      echo
      if [ "$p1" = "$p2" ]; then
        ADMIN_PASSWORD="$p1"
        break
      fi
      echo "  Doesn't match. Try again."
    done
  fi

  GENERATED_ADMIN_PASS=""
  if [ -z "$ADMIN_PASSWORD" ]; then
    ADMIN_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(12))')"
    GENERATED_ADMIN_PASS="$ADMIN_PASSWORD"
  fi

  SECRET="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  cat > .env <<EOF
ENVIRONMENT=production

DATABASE_URL=sqlite:///./nvr.db

ALLOWED_ORIGINS=http://localhost,http://localhost:${PORT}
CORS_ORIGIN_REGEX=^https?://(localhost|127\\.0\\.0\\.1|.*\\.local|192\\.168\\.\\d+\\.\\d+|10\\.\\d+\\.\\d+\\.\\d+|172\\.(1[6-9]|2[0-9]|3[01])\\.\\d+\\.\\d+)(:\\d+)?$

FFMPEG_PATH=ffmpeg
HLS_SEGMENT_SECONDS=2
HLS_LIST_SIZE=5
MAX_CONCURRENT_STREAMS=4

RECORDING_SEGMENT_MINUTES=10
RETENTION_DAYS=7

SECRET_KEY=$SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_PASSWORD=$ADMIN_PASSWORD
EOF
else
  log "Reusing existing backend/.env"
  GENERATED_ADMIN_PASS=""
fi

log "Running database migrations"
./venv/bin/alembic upgrade head

# -------- 3. Frontend ---------------------------------------------------------
log "Building frontend (takes a few minutes on a Pi)"
cd "$PROJECT_DIR/frontend"
npm install --silent
npm run build

# -------- 4. Systemd service --------------------------------------------------
log "Installing systemd service: ${SERVICE_NAME}.service"
sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null <<EOF
[Unit]
Description=Pi NVR
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR/backend
ExecStart=$PROJECT_DIR/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service" >/dev/null
sudo systemctl restart "${SERVICE_NAME}.service"

# Give it a moment to come up, then check health.
sleep 2
if ! systemctl is-active --quiet "${SERVICE_NAME}.service"; then
  echo ""
  echo "Service failed to start. Check logs with:"
  echo "  sudo journalctl -u ${SERVICE_NAME}.service -e --no-pager"
  exit 1
fi

# -------- 5. Done -------------------------------------------------------------
HOST_LOCAL="$(hostname).local"
HOST_IP="$(hostname -I 2>/dev/null | awk '{print $1}' || echo unknown)"

echo ""
echo "============================================================"
echo " Pi NVR is up and running."
echo "------------------------------------------------------------"
echo "  http://${HOST_LOCAL}:${PORT}"
echo "  http://${HOST_IP}:${PORT}"
if [ -n "${GENERATED_ADMIN_PASS:-}" ]; then
  echo ""
  echo "  Admin login:   ${ADMIN_USERNAME:-admin}"
  echo "  Password:      $GENERATED_ADMIN_PASS    (auto-generated)"
  echo ""
  echo "  Save it. Also stored in $PROJECT_DIR/backend/.env"
elif [ -n "${ADMIN_USERNAME:-}" ]; then
  echo ""
  echo "  Admin login:   $ADMIN_USERNAME  (password set during install)"
fi
echo "------------------------------------------------------------"
echo "  Logs:          sudo journalctl -u ${SERVICE_NAME}.service -f"
echo "  Restart:       sudo systemctl restart ${SERVICE_NAME}.service"
echo "  Stop:          sudo systemctl stop ${SERVICE_NAME}.service"
echo "  Disable boot:  sudo systemctl disable ${SERVICE_NAME}.service"
echo "============================================================"
