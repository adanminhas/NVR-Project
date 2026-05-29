# Network Video Recorder (NVR) Project

A custom Network Video Recorder built to manage IP camera streams from a
Raspberry Pi (or any small Linux box), using a FastAPI backend and a Vue 3
frontend. Designed for DIY home surveillance.

## Features

- Multi-camera management — add, edit, delete cameras via the UI
- Live view in any browser via HLS (works on iOS Safari, Android, desktop)
- Continuous recording to MP4 segments with retention sweep
- Recordings page with date filter, inline playback, download, delete
- Username + password auth with JWTs; admin-managed user accounts
- RTSP credentials masked in API responses
- Mobile-friendly UI (hamburger menu, tap-friendly buttons)
- One-shot Pi installer that sets everything up and auto-starts on boot

## Tech stack

FastAPI · SQLAlchemy · Alembic · SQLite (or MySQL) · ffmpeg · Vue 3 · Vite ·
hls.js · systemd.

## Install on a Raspberry Pi

End-to-end setup, from blank SD card to logging in. Targets Raspberry Pi OS
Lite (64-bit, Bookworm) on a Pi 4 or 5. Also works on any Debian/Ubuntu host.

### What you'll need

- Raspberry Pi 4 or 5 (Pi 3 works but the frontend build is slow; Pi Zero W
  doesn't have enough RAM)
- microSD card (16 GB+, Class 10 or better)
- Power supply
- A computer to flash the SD card and SSH in
- Wi-Fi credentials, or an Ethernet cable
- Optional: USB SSD if you plan to record many cameras 24/7

### 1. Flash the SD card

Install [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your
computer, then:

1. **Device** — select your Pi model.
2. **Operating System** — Raspberry Pi OS (other) → **Raspberry Pi OS Lite (64-bit)**.
3. **Storage** — select your SD card.
4. Click **Next**, then **Edit Settings**. On the **General** tab set hostname
   (e.g. `pi-nvr` — you'll reach the Pi at that name), username, password,
   Wi-Fi, locale. On the **Services** tab enable **SSH**.
5. **Save** and write the image.

Eject the SD card, put it in the Pi.

### 2. First boot

Plug the Pi in. Wait ~60 seconds for it to boot and join Wi-Fi.

### 3. SSH in

From your computer:

```bash
ssh <your-username>@pi-nvr
```

(If the bare hostname doesn't resolve, try `pi-nvr.local` — that uses mDNS
via Avahi. If neither resolves, find the Pi's IP in your router's admin page
and use that instead.)

### 4. Run the installer

```bash
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/adanminhas/NVR-Project ~/pi-nvr
cd ~/pi-nvr
bash scripts/install_pi.sh
```

Takes ~5–10 minutes on a Pi 4. It prompts for an admin username (default
`admin`) and password (hidden as you type — press Enter to auto-generate one).

The installer does everything: installs system packages, sets up Python,
builds the frontend, configures SQLite, runs migrations, creates the admin
user, and registers a systemd service that auto-starts on every boot.

When it finishes you'll see:

```
============================================================
 Pi NVR is up and running.
------------------------------------------------------------
  http://pi-nvr:8000
  http://192.168.1.61:8000
  Admin login:   admin  (password set during install)
============================================================
```

### 5. Log in

Open the URL on any device on the same network — laptop, phone, tablet. Sign
in with the username and password you set.

If you need to recover or change the admin password later, edit
`~/pi-nvr/backend/.env` and `sudo systemctl restart pi-nvr`.

### Auto-start on boot

The installer registers a systemd unit and enables it, so the NVR comes back
up automatically every time the Pi powers on — no SSH, no manual steps.

Specifically, the unit:

- Is `enabled` for `multi-user.target`, so systemd starts it on every boot
- Waits for the network to actually come up (`network-online.target`) before
  launching uvicorn, so it doesn't fail trying to bind before Wi-Fi connects
- Restarts itself 5 seconds after any crash (`Restart=on-failure`)
- Logs to `journald` so the full history survives reboots

Verify it's enabled:

```bash
systemctl is-enabled pi-nvr   # should print "enabled"
```

Test it end-to-end by rebooting the Pi:

```bash
sudo reboot
```

Wait ~30 seconds, then open `http://pi-nvr:8000` from your laptop. It should
be back up with no intervention.

## Managing the service

| Command | What it does |
|---|---|
| `sudo systemctl status pi-nvr` | Current state |
| `sudo systemctl restart pi-nvr` | Restart (after editing `.env`, etc.) |
| `sudo systemctl stop pi-nvr` | Stop |
| `sudo systemctl disable pi-nvr` | Don't auto-start on boot anymore |
| `sudo journalctl -u pi-nvr -f` | Tail logs live |

## Updating to a new release

Whenever new features ship to the repo, on the Pi:

```bash
ssh <user>@pi-nvr
cd ~/pi-nvr
git pull
bash scripts/install_pi.sh
```

The installer is idempotent — it reuses the existing venv and `.env`,
re-installs only what's changed, applies any new migrations, rebuilds the
frontend, and restarts the service.

If a new release adds new settings, you'll need to copy the new keys from
`backend/.env.example` into your existing `backend/.env` manually (the
installer never overwrites your `.env`). Then `sudo systemctl restart pi-nvr`.

To roll back a broken release:

```bash
cd ~/pi-nvr
git log --oneline -n 10        # find the commit you want
git checkout <commit-hash>
bash scripts/install_pi.sh
```

## Streaming protocol

This is the **HLS (HTTP Live Streaming) version**. HLS was chosen because it
works in any modern browser via [hls.js](https://github.com/video-dev/hls.js/)
and needs only a static file server in front of ffmpeg output.

The trade-off is latency: live view sits ~5–10 seconds behind real time. Fine
for "what just happened" surveillance; not for real-time monitoring. A
separate **WebRTC version** is planned for sub-second latency.

## Authentication

The API is protected with username/password login backed by JWTs. The first
user is the bootstrap admin created during install. Admins can create
additional users (admin or normal) from the **Users** page in the UI.

RTSP credentials are masked (`rtsp://***:***@host/...`) in API responses so
they don't leak into the browser console or logs.

**Limitation:** the raw HLS segment files served at `/streams/<camera>/...`
are not gated by JWT (browser `<video>` tags don't send Authorization
headers). For a LAN-only deployment this is acceptable; for anything
internet-facing, put a reverse proxy with its own auth in front, or move to
the planned WebRTC variant. Recording playback (`/api/recordings/{id}/file`)
*is* protected — it accepts a short-lived token via query string.

## Storage

Recordings are written to `backend/recordings/<camera_id>/` as MP4 segments
(default 10 minutes each). The retention sweeper runs on startup and deletes
files older than `RETENTION_DAYS` (default 7). For heavy 24/7 recording,
mount a USB SSD at `backend/recordings/` — the Pi's SD card will wear out
otherwise.

## Status

v1 complete (HLS streaming, recording, multi-user auth, Pi installer).
Planned: WebRTC variant for low-latency live view; scheduled and
motion-triggered recording.

## Author

**Adan Minhas**
Computer Science student at Queen Mary University of London
GitHub: <https://github.com/adanminhas>

---

## Development

For contributors / hacking on the code locally. Skip this section if you're
just installing on a Pi.

### Running locally

Prereqs: Python 3.12, Node 18+, ffmpeg, optionally MySQL/MariaDB. SQLite works
out of the box and needs no setup.

```bash
# Backend
cd backend
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
cp .env.dev .env             # SQLite config; or write your own for MySQL
../scripts/migrate.sh

# Frontend
cd ../frontend
npm install
cp .env.example .env

# Run (two terminals)
./scripts/dev_backend.sh
./scripts/dev_frontend.sh
```

UI at <http://localhost:5173>. API at <http://localhost:8000>. Default admin
created from `.env`.

### Tests, lint, format

```bash
# Backend
cd backend
./venv/bin/python -m pytest
./venv/bin/ruff check app tests
./venv/bin/ruff format app tests

# Frontend
cd frontend
npm test
npm run lint
npm run format
```

CI (GitHub Actions) runs all of these on every push.

### Adding a migration

After changing a SQLAlchemy model:

```bash
./scripts/new_migration.sh "add some column"
# review the generated file in backend/alembic/versions/
./scripts/migrate.sh
```

### Releasing an update to the Pi

```bash
# Test locally first
cd backend && ./venv/bin/python -m pytest
cd ../frontend && npm test && npm run lint
# Then push
git push
```

Then on the Pi, follow the "Updating to a new release" section above.

### Using MySQL instead of SQLite

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

Restart the backend.
