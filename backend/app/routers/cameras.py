from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.camera_model import Camera
from app.schemas import (
    CameraCreate,
    CameraOut,
    CameraUpdate,
    MASKED_CREDS,
    RecordingModeUpdate,
)
from app.services import auth_service, recording_service, stream_service

router = APIRouter(
    prefix="/api/cameras",
    tags=["Cameras"],
    dependencies=[Depends(auth_service.get_current_user)],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _apply_recording_mode(camera: Camera, mode: str) -> None:
    if mode == camera.recording_mode:
        return
    camera.recording_mode = mode
    if mode == "continuous":
        recording_service.start_recording(camera.id, camera.rtsp_url)
    else:
        recording_service.stop_recording(camera.id)


@router.get("/", response_model=List[CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).all()


@router.get("/{camera_id}", response_model=CameraOut)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found",
        )
    return camera


@router.post("/", response_model=CameraOut, status_code=status.HTTP_201_CREATED)
def create_camera(camera_in: CameraCreate, db: Session = Depends(get_db)):
    camera = Camera(
        name=camera_in.name,
        rtsp_url=camera_in.rtsp_url,
        status="offline",
        recording_mode="off",
    )
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.put("/{camera_id}", response_model=CameraOut)
def update_camera(
    camera_id: int,
    camera_in: CameraUpdate,
    db: Session = Depends(get_db),
):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found",
        )

    if camera_in.name is not None:
        camera.name = camera_in.name
    if camera_in.rtsp_url is not None and MASKED_CREDS not in camera_in.rtsp_url:
        # If recording is active, restart it so ffmpeg picks up the new URL.
        was_recording = camera.recording_mode == "continuous"
        camera.rtsp_url = camera_in.rtsp_url
        if was_recording:
            recording_service.stop_recording(camera.id)
            recording_service.start_recording(camera.id, camera.rtsp_url)
    if camera_in.status is not None:
        camera.status = camera_in.status
    if camera_in.recording_mode is not None:
        _apply_recording_mode(camera, camera_in.recording_mode)

    db.commit()
    db.refresh(camera)
    return camera


@router.put("/{camera_id}/recording-mode", response_model=CameraOut)
def set_recording_mode(
    camera_id: int,
    payload: RecordingModeUpdate,
    db: Session = Depends(get_db),
):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found",
        )

    _apply_recording_mode(camera, payload.mode)
    db.commit()
    db.refresh(camera)
    return camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found",
        )

    stream_service.delete_stream_dir(camera.id)
    recording_service.delete_recording_dir(camera.id)

    db.delete(camera)
    db.commit()
    return None
