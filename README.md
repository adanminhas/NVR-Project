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
recording, UI enhancements, proper Alembic migrations, automated tests, and
a WebRTC streaming variant for low-latency live view.

## Author
**Adan Minhas**  
Computer Science student at Queen Mary University of London  
GitHub: https://github.com/adanminhas
