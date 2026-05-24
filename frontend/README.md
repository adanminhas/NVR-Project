# Pi NVR — Frontend

Vue 3 + Vite client for the Pi NVR backend. Lists cameras, manages them, and
plays live HLS streams via [hls.js](https://github.com/video-dev/hls.js/).

## Prerequisites

- Node.js 18+ and npm
- The backend running and reachable (default: `http://localhost:8000`)

## Setup

```bash
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if your backend lives elsewhere
npm run dev
```

The dev server defaults to <http://localhost:5173>.

## Environment

| Variable             | Default                 | Purpose                                    |
| -------------------- | ----------------------- | ------------------------------------------ |
| `VITE_API_BASE_URL`  | `http://localhost:8000` | Backend origin used by axios and HLS URLs. |

Vite only exposes variables prefixed with `VITE_` to client-side code.

## Scripts

| Command           | Description                                |
| ----------------- | ------------------------------------------ |
| `npm run dev`     | Start the Vite dev server with HMR.        |
| `npm run build`   | Production build into `dist`.              |
| `npm run preview` | Serve the production build locally.        |

## Project structure

```
src/
  api/
    client.js       axios instance with VITE_API_BASE_URL
    cameras.js      camera CRUD endpoints
    streams.js      start/stop/health + HLS playlist URL helper
  components/
    NavBar.vue
    Modal.vue
    CameraForm.vue
  pages/
    CameraList.vue  list + add/edit/delete + start/stop
    LiveView.vue    HLS player with diagnostics overlay
  router.js
  main.js
  style.css         global dark blue theme via CSS variables
```

## Deploying to a different host

Set `VITE_API_BASE_URL` in `.env` to the backend's reachable URL, then build:

```bash
VITE_API_BASE_URL=http://nvr.local:8000 npm run build
```

Serve the contents of `dist/` from any static host. Make sure the backend's
`ALLOWED_ORIGINS` includes the origin you're serving from.
