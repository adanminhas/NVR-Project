from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.camera_model import Camera
from app.services import stream_service

router = APIRouter(
    prefix="/api/streams",
    tags=["Streams"],
)


# Shared DB dependency (same pattern as in cameras.py)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{camera_id}/start")
def start_camera_stream(camera_id: int, db: Session = Depends(get_db)):
    """
    Start HLS streaming for a given camera.
    """
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found",
        )

    if not camera.rtsp_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera has no RTSP URL configured",
        )

    playlist_path = stream_service.start_stream(camera.id, camera.rtsp_url)

    # Update status in DB (simple for now)
    camera.status = "streaming"
    db.commit()
    db.refresh(camera)

    # This is the URL the frontend will later load in a video player
    playlist_url = f"/streams/{camera.id}/index.m3u8"

    return {
        "message": "Stream started",
        "camera_id": camera.id,
        "status": camera.status,
        "playlist_url": playlist_url,
    }


@router.post("/{camera_id}/stop")
def stop_camera_stream(camera_id: int, db: Session = Depends(get_db)):
    """
    Stop HLS streaming for a given camera.
    """
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found",
        )

    stopped = stream_service.stop_stream(camera.id)
    if stopped:
        camera.status = "stopped"
        db.commit()
        db.refresh(camera)

    return {
        "message": "Stream stopped" if stopped else "No running stream to stop",
        "camera_id": camera.id,
        "status": camera.status,
    }

@router.get("/{camera_id}/health")
def stream_health(camera_id: int):
    running = stream_service.is_stream_running(camera_id)
    active = stream_service.is_hls_active(camera_id)

    return {
        "camera_id": camera_id,
        "ffmpeg_running": running,
        "hls_active": active,
    }
