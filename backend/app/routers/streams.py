from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.camera_model import Camera
from app.services import stream_service
from app.services.stream_service import StreamLimitExceeded

router = APIRouter(
    prefix="/api/streams",
    tags=["Streams"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{camera_id}/start")
def start_camera_stream(camera_id: int, db: Session = Depends(get_db)):
    """Start HLS streaming for a given camera."""
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

    try:
        stream_service.start_stream(camera.id, camera.rtsp_url)
    except StreamLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        )

    camera.status = "streaming"
    db.commit()
    db.refresh(camera)

    return {
        "message": "Stream started",
        "camera_id": camera.id,
        "status": camera.status,
        "playlist_url": f"/streams/{camera.id}/index.m3u8",
    }


@router.post("/{camera_id}/stop")
def stop_camera_stream(camera_id: int, db: Session = Depends(get_db)):
    """Stop HLS streaming for a given camera."""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found",
        )

    stopped = stream_service.stop_stream(camera.id)

    # Stop is idempotent: even if no tracked process existed (e.g. backend
    # restarted), the camera is functionally stopped now, so reflect that.
    camera.status = "stopped"
    db.commit()
    db.refresh(camera)

    return {
        "message": "Stream stopped" if stopped else "Stream was not running",
        "camera_id": camera.id,
        "status": camera.status,
    }


@router.get("/{camera_id}/health")
def stream_health(camera_id: int):
    health = stream_service.get_stream_health(camera_id)
    # Keep the legacy field so the existing frontend keeps working.
    health["hls_active"] = stream_service.is_hls_active(camera_id)
    return health
