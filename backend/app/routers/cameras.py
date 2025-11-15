from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.camera_model import Camera

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

@router.get("/")
def list_cameras(db: Session = Depends(get_db)):
    cameras = db.query(Camera).all()
    return cameras
