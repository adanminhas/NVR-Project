from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.recording_model import Recording
from app.schemas import RecordingOut
from app.services import recording_service

router = APIRouter(
    prefix="/api/recordings",
    tags=["Recordings"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[RecordingOut])
def list_recordings(
    camera_id: Optional[int] = Query(None),
    start_from: Optional[datetime] = Query(None),
    start_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    return recording_service.list_recordings(
        db,
        camera_id=camera_id,
        start_from=start_from,
        start_to=start_to,
    )


@router.get("/{recording_id}", response_model=RecordingOut)
def get_recording(recording_id: int, db: Session = Depends(get_db)):
    rec = db.query(Recording).filter(Recording.id == recording_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found",
        )
    return rec


@router.get("/{recording_id}/file")
def download_recording(recording_id: int, db: Session = Depends(get_db)):
    rec = db.query(Recording).filter(Recording.id == recording_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found",
        )
    path = Path(rec.file_path)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File no longer on disk",
        )
    return FileResponse(
        path,
        media_type="video/mp4",
        filename=path.name,
    )


@router.delete("/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recording(recording_id: int, db: Session = Depends(get_db)):
    rec = db.query(Recording).filter(Recording.id == recording_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found",
        )
    path = Path(rec.file_path)
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
    db.delete(rec)
    db.commit()
    return None
