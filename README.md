# Network Video Recorder (NVR) Project

A custom Network Video Recorder (NVR) system built to manage IP camera video streams using a FastAPI backend and a web-based frontend.

This project is designed to be used as part of a DIY home surveillance system.

## Features
- Manage and monitor multiple IP camera streams
- Live video streaming and recording using FFmpeg
- Automatic stream health checks and recovery
- HLS (HTTP Live Streaming) support
- Web-based frontend for live viewing and control

## Tech Stack
**Backend**
- Python
- FastAPI
- FFmpeg
- Linux

**Frontend**
- Vue.js
- HTML / CSS / JavaScript

## Architecture Overview
- FastAPI backend manages camera configuration and stream control
- FFmpeg handles video ingestion, transcoding, and HLS output
- Health check system monitors streams and automatically restarts failed processes
- Frontend communicates with backend via REST APIs to display live streams

## Setup

### Prerequisites

- Python 3.12 (Python 3.14 has no numpy wheels yet — not strictly required by
  this project, but worth knowing)
- Node.js 18+ and npm
- FFmpeg available on `PATH` (`ffmpeg -version` to verify)
- **Either** MySQL/MariaDB **or** SQLite (no server needed) for the database

### One-time setup

```bash
# Clone, then from the project root:
cd backend
python3.12 -m venv venv
./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -r requirements.txt

# Pick a database — see the two options below.
# Then run migrations:
../scripts/migrate.sh

# Frontend:
cd ../frontend
npm install
cp .env.example .env  # tweak VITE_API_BASE_URL if needed
```

### Database option A — MySQL/MariaDB

```sql
-- as the MySQL root user:
CREATE DATABASE nvr CHARACTER SET utf8mb4;
CREATE USER 'nvr'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON nvr.* TO 'nvr'@'localhost';
FLUSH PRIVILEGES;
```

Then in `backend/.env`:

```
DATABASE_URL=mysql+pymysql://nvr:your-strong-password@localhost/nvr
```

### Database option B — SQLite (zero-setup local dev)

Easiest for local hacking. No server, no users, no grants:

```bash
cp backend/.env.dev backend/.env
```

That template uses `DATABASE_URL=sqlite:///./nvr.db`. The file lives next to
the `backend/` directory and is gitignored.

### Run it

Two terminals:

```bash
# Terminal 1 — backend (also runs Alembic migrations on startup)
./scripts/dev_backend.sh

# Terminal 2 — frontend
./scripts/dev_frontend.sh
```

UI at <http://localhost:5173>. The bootstrap admin user is created from
`ADMIN_USERNAME` / `ADMIN_PASSWORD` in `backend/.env` on first start.

### Migrations

Migrations live in `backend/alembic/versions/` and run automatically on
backend startup. For existing databases predating Alembic (e.g. set up via
this project's earlier hand-rolled migrations), the first start does an
`alembic stamp head` to adopt the schema as the baseline without touching
DDL; subsequent starts run `alembic upgrade head` normally.

To add a new migration after changing a SQLAlchemy model:

```bash
./scripts/new_migration.sh "add some column"
# review the generated file in backend/alembic/versions/
./scripts/migrate.sh
```

Or manually:

```bash
cd backend
./venv/bin/alembic revision --autogenerate -m "describe change"
./venv/bin/alembic upgrade head
```

## Deploying to a Raspberry Pi

One-shot installer for a fresh Raspberry Pi OS Lite (64-bit, Bookworm). Also
works on any Debian/Ubuntu host.

```bash
# On the Pi, after SSH'ing in:
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/adanminhas/NVR-Project ~/pi-nvr
cd ~/pi-nvr
bash scripts/install_pi.sh
```

The script:

- Installs system packages: `python3`, `python3-venv`, `ffmpeg`, Node 20,
  `avahi-daemon` (so the Pi is reachable at `<hostname>.local`).
- Sets up the backend venv and installs Python dependencies.
- Writes `backend/.env` with a random `SECRET_KEY`, SQLite as the database (no
  MySQL server needed), and a CORS regex that permits LAN IPs.
- Asks for an admin username and password (defaults to `admin`, password
  hidden). If you'd rather automate or pipe the script through `curl`, see
  the non-interactive option below.
- Runs Alembic migrations and creates the admin user on first start.
- Builds the frontend with `npm run build`. The backend serves the built
  files directly, so there's no separate frontend service in production.
- Registers a systemd unit `pi-nvr.service` that auto-starts on boot, restarts
  on failure, and logs to `journald`.

When it finishes it prints the URL to open. If you entered an admin password
during the prompt, it's not echoed back; if you let the script auto-generate
one (or it was non-interactive), it's printed once. Either way, you can
recover or change it later by editing `backend/.env` and restarting the
service.

### Non-interactive / scripted install

Pass credentials as environment variables to skip the prompt:

```bash
ADMIN_USERNAME=myuser ADMIN_PASSWORD=mypass bash scripts/install_pi.sh
```

Useful for cloud-init, Ansible, or pre-baked SD images.

### Managing the service

| Command | What it does |
|---|---|
| `sudo systemctl status pi-nvr` | Current state |
| `sudo systemctl restart pi-nvr` | Restart (after editing `.env`, etc.) |
| `sudo systemctl stop pi-nvr` | Stop |
| `sudo systemctl disable pi-nvr` | Don't auto-start on boot anymore |
| `sudo journalctl -u pi-nvr -f` | Tail logs live |

### Updating after a `git pull`

```bash
cd ~/pi-nvr
git pull
bash scripts/install_pi.sh   # idempotent — rebuilds frontend, runs new migrations
```

The script reuses your existing venv and `.env`, only installs system packages
if missing, and re-runs Alembic to apply any new migrations.

### Notes

- **Pi 4 / Pi 5 only really.** Pi 3 works but the frontend build takes ~3 minutes
  on first install. Pi Zero W is too underpowered (1GB RAM is the practical floor
  for `npm run build`).
- **First-frame latency is HLS-bound** (~5–10s). See "Streaming protocol".
- **Storage:** recordings accumulate under `backend/recordings/`. Default
  `RETENTION_DAYS=7` sweeps older files on startup. If you record many cameras
  you'll want an external SSD on USB — the SD card will wear out eventually.

## Motivation
This project was built to gain hands-on experience with backend systems, video streaming, and full-stack development.  
An additional motivation was to deploy the system as part of a personal DIY home surveillance setup, allowing direct practical use and real-world testing of reliability, performance, and fault tolerance.

## Streaming protocol

This is the **HLS (HTTP Live Streaming) version** of the project. HLS was
chosen for v1 because it works in any modern browser via
[hls.js](https://github.com/video-dev/hls.js/), needs only a static file
server in front of ffmpeg output, and keeps the implementation simple while
the rest of the system (camera CRUD, recording, auth, UI) is built out.

The trade-off is latency: live view sits roughly 5–10 seconds behind real
time, which is normal for HLS and fine for "review what just happened"
surveillance use cases. A separate **WebRTC version** is planned for sub-second
latency once v1 is feature-complete, likely as a sidecar bridge (e.g.
[`go2rtc`](https://github.com/AlexxIT/go2rtc) or
[`mediamtx`](https://github.com/bluenviron/mediamtx)) exposing the same
cameras over WebRTC, with the frontend selecting protocol per view.

## Authentication

The API is protected with username/password login backed by JWTs. On first
startup the backend creates a bootstrap user from the `ADMIN_USERNAME` and
`ADMIN_PASSWORD` values in `backend/.env`. Change these (or replace the user
via SQL) before exposing the service beyond your local machine.

RTSP credentials are masked (`rtsp://***:***@host/...`) in API responses so
they don't leak into the browser console or logs. The full URL is still
stored on the server. The edit form treats an unchanged masked URL as
"no change", so you can edit a camera's name without re-entering its
credentials.

**Known limitation:** HLS segment files (`/streams/<camera>/index.m3u8` and
the `.ts` chunks) are served via FastAPI's `StaticFiles` mount and are *not*
gated by JWT. Browsers' `<video>` tags don't send `Authorization` headers
on segment XHRs, so protecting those would require signed URLs or a cookie-
based auth model. For a LAN-only deployment behind a router this is
acceptable; for any internet-facing deployment add a reverse proxy with
its own auth, or move to the planned WebRTC variant where authentication
is done at signaling time. Recording playback (`/api/recordings/{id}/file`)
*is* protected, via a short-lived token in the query string.

## Status
Active development — planned improvements include scheduled/motion-based
recording, UI enhancements, automated tests, and a WebRTC streaming variant
for low-latency live view.

## Author
**Adan Minhas**  
Computer Science student at Queen Mary University of London  
GitHub: https://github.com/adanminhas
