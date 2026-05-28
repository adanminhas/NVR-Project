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

End-to-end setup guide, from a blank SD card to logging in. Targets Raspberry
Pi OS Lite (64-bit, Bookworm) on a Pi 4 or Pi 5. Pi 3 works but the frontend
build is slow; Pi Zero W doesn't have enough RAM.

### What you'll need

- Raspberry Pi 4 or 5
- microSD card (16 GB+, Class 10 or better)
- Power supply for the Pi
- Computer to flash the SD card and SSH in
- Wi-Fi credentials, or an Ethernet cable
- (Optional) USB SSD if you plan to record many cameras

### 1. Flash the SD card

Install [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your
computer and launch it.

1. **Device:** select your Pi model.
2. **Operating System:** Raspberry Pi OS (other) → **Raspberry Pi OS Lite (64-bit)**.
3. **Storage:** select the SD card.
4. Click **Next**, then **Edit Settings** in the "Apply OS customisation" dialog.
   On the **General** tab:
   - Set hostname (e.g. `pi-nvr` — this is the name you'll use to reach it)
   - Set username and password
   - Configure Wi-Fi (SSID + password)
   - Set locale and timezone
   On the **Services** tab:
   - Enable **SSH** (password or public key, your call)
5. **Save**, then write the image.

When it finishes, eject the SD card and put it in the Pi.

### 2. First boot

Plug the Pi in. Wait ~60 seconds for it to boot and join Wi-Fi. The Pi will
announce itself on the network via mDNS using the hostname you set.

### 3. SSH in

From your computer:

```bash
ssh <your-username>@pi-nvr.local
```

(Replace `pi-nvr` with whatever hostname you set. If `.local` doesn't resolve —
some routers block mDNS — find the Pi's IP in your router's admin page and use
that instead.)

### 4. Clone and install

On the Pi:

```bash
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/adanminhas/NVR-Project ~/pi-nvr
cd ~/pi-nvr
bash scripts/install_pi.sh
```

Takes ~5–10 minutes on a Pi 4. It will prompt for an admin username (default
`admin`) and password (hidden as you type; press Enter to auto-generate one).

The script handles everything: system packages (Python, Node 20, ffmpeg,
avahi for mDNS), the backend venv, the SQLite database, Alembic migrations,
the frontend build, and a systemd service that auto-starts on boot.

When it finishes you'll see something like:

```
============================================================
 Pi NVR is up and running.
------------------------------------------------------------
  http://pi-nvr.local:8000
  http://192.168.1.61:8000

  Admin login:   admin  (password set during install)
============================================================
```

### 5. Log in

Open the URL on any device on the same network — laptop, phone, tablet. Sign
in with the username and password you chose during install.

That's it. The service is now running and will auto-start every time the Pi
boots. If you ever need to recover or change the admin password, edit
`~/pi-nvr/backend/.env` and `sudo systemctl restart pi-nvr`.

### Non-interactive / scripted install

If you want to skip the prompts (cloud-init, Ansible, pre-baked image, etc.),
pass credentials as environment variables:

```bash
ADMIN_USERNAME=myuser ADMIN_PASSWORD=mypass bash scripts/install_pi.sh
```

### Managing the service

| Command | What it does |
|---|---|
| `sudo systemctl status pi-nvr` | Current state |
| `sudo systemctl restart pi-nvr` | Restart (after editing `.env`, etc.) |
| `sudo systemctl stop pi-nvr` | Stop |
| `sudo systemctl disable pi-nvr` | Don't auto-start on boot anymore |
| `sudo journalctl -u pi-nvr -f` | Tail logs live |

### Rolling out updates

When you ship a new feature (a settings page, say), the cycle is:

**On your dev machine:**

```bash
# edit code, run tests
cd backend && ./venv/bin/python -m pytest
cd ../frontend && npm test && npm run lint
# happy with it?
git add -A
git commit -m "feat: new shiny thing"
git push
```

**On the Pi:**

```bash
ssh <user>@pi-nvr.local
cd ~/pi-nvr
git pull
bash scripts/install_pi.sh
sudo systemctl restart pi-nvr      # in case install didn't already restart it
```

That's it. The install script is **idempotent** and handles each kind of
change without needing options:

| What changed | What the script does |
|---|---|
| Frontend (Vue, CSS) | `npm run build` regenerates `frontend/dist/`; backend serves the new files immediately |
| Backend Python code | venv stays the same; systemd `restart` reloads the new code |
| `requirements.txt` | `pip install -r requirements.txt` picks up the new deps (existing ones are skipped) |
| `package.json` | `npm install` picks up new JS deps |
| New Alembic migration in `backend/alembic/versions/` | `alembic upgrade head` runs the new revisions in order against your real SQLite database |
| New keys in `.env.example` | **not auto-merged** — the script leaves your existing `.env` alone. Diff `backend/.env.example` against `backend/.env` and add missing keys manually, then restart |
| System packages | `apt-get install -y` is a no-op when already present |

**Verifying after an update:**

```bash
sudo systemctl status pi-nvr           # should say "active (running)"
sudo journalctl -u pi-nvr -n 50 --no-pager   # last 50 log lines
```

If something goes wrong, the previous logs are still in `journald` —
`journalctl -u pi-nvr --since "1 hour ago"` shows the full timeline.

**Rolling back:** if a deploy breaks something, on the Pi:

```bash
cd ~/pi-nvr
git log --oneline -n 5     # find the commit hash you want to go back to
git checkout <hash>
bash scripts/install_pi.sh
sudo systemctl restart pi-nvr
```

Then push a fix from your dev machine and `git checkout main && git pull` to
re-sync.

**Skipping the full reinstall.** If you know only frontend or only backend
changed, you can skip parts of the script and just do what's needed:

```bash
# Frontend-only change
cd ~/pi-nvr/frontend && npm install && npm run build
sudo systemctl restart pi-nvr

# Backend-only Python change (no new deps, no new migration)
sudo systemctl restart pi-nvr

# New migration only
cd ~/pi-nvr/backend && ./venv/bin/alembic upgrade head
sudo systemctl restart pi-nvr
```

Running the full `install_pi.sh` is always safe and easier to remember,
though.

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
