from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import SessionLocal
from app.db_migrations import run_migrations
from app.models.camera_model import Camera
from app.routers import auth, cameras, recordings, streams, users
from app.services import auth_service, recording_service, stream_service
from app.settings import settings


def _reset_camera_states_on_startup() -> None:
    """
    After a backend restart we have no live ffmpeg processes, so any camera
    DB status of 'streaming' is stale. Reset to 'offline' and wipe leftover
    segments from prior sessions. Continuous recordings are re-spawned.
    """
    db = SessionLocal()
    try:
        cameras_in_db = db.query(Camera).all()
        for camera in cameras_in_db:
            if camera.status == "streaming":
                camera.status = "offline"
            stream_service._cleanup_segments(camera.id)
            if camera.recording_mode == "continuous":
                recording_service.start_recording(camera.id, camera.rtsp_url)
        db.commit()
        recording_service.sweep_retention(db)
    finally:
        db.close()


def _bootstrap_admin_user() -> None:
    db = SessionLocal()
    try:
        auth_service.ensure_admin_user(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    run_migrations()
    _bootstrap_admin_user()
    _reset_camera_states_on_startup()
    yield


app = FastAPI(title="Pi NVR Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/streams", StaticFiles(directory=settings.streams_dir), name="streams")

app.include_router(auth.router)
app.include_router(cameras.router)
app.include_router(streams.router)
app.include_router(recordings.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "Pi NVR Backend Running!"}
