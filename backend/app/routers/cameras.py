from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.camera_model import Camera
from app.schemas import CameraCreate, CameraUpdate, CameraOut

router = APIRouter(
    prefix="/api/cameras",
    tags=["Cameras"]
)

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== CRUD endpoints ==========

# 1) List all cameras
@router.get("/", response_model=List[CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    cameras = db.query(Camera).all()
    return cameras


# 2) Get a single camera by ID
@router.get("/{camera_id}", response_model=CameraOut)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found",
        )
    return camera


# 3) Create a new camera
@router.post("/", response_model=CameraOut, status_code=status.HTTP_201_CREATED)
def create_camera(camera_in: CameraCreate, db: Session = Depends(get_db)):
    camera = Camera(
        name=camera_in.name,
        rtsp_url=camera_in.rtsp_url,
        status="offline",  # default until you implement health checks
    )
    db.add(camera)
    db.commit()
    db.refresh(camera)  # refresh to get the new ID from DB
    return camera


# 4) Update an existing camera
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

    # Update only the fields that were provided
    if camera_in.name is not None:
        camera.name = camera_in.name
    if camera_in.rtsp_url is not None:
        camera.rtsp_url = camera_in.rtsp_url
    if camera_in.status is not None:
        camera.status = camera_in.status

    db.commit()
    db.refresh(camera)
    return camera


# 5) Delete a camera
@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found",
        )

    db.delete(camera)
    db.commit()
    # 204 No Content -> nothing returned
    return None
