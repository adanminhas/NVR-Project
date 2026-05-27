from datetime import datetime
from pathlib import Path

import jwt
from app.database import SessionLocal
from app.models.recording_model import Recording
from app.models.user_model import User
from app.schemas import RecordingOut
from app.services import auth_service, recording_service
from app.settings import settings
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

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


def _verify_query_token(token: str, db: Session) -> User:
    creds_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        if not username:
            raise creds_error
    except jwt.PyJWTError as exc:
        raise creds_error from exc
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise creds_error
    return user


@router.get("/", response_model=list[RecordingOut])
def list_recordings(
    camera_id: int | None = Query(None),
    start_from: datetime | None = Query(None),
    start_to: datetime | None = Query(None),
    db: Session = Depends(get_db),
    _user: User = Depends(auth_service.get_current_user),
):
    return recording_service.list_recordings(
        db,
        camera_id=camera_id,
        start_from=start_from,
        start_to=start_to,
    )


@router.get("/{recording_id}", response_model=RecordingOut)
def get_recording(
    recording_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(auth_service.get_current_user),
):
    rec = db.query(Recording).filter(Recording.id == recording_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found",
        )
    return rec


@router.get("/{recording_id}/file")
def download_recording(
    recording_id: int,
    token: str = Query(..., description="JWT, supplied via query string for <video> playback"),
    db: Session = Depends(get_db),
):
    # <video> tags can't carry Authorization headers; accept token via query string.
    _verify_query_token(token, db)

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
def delete_recording(
    recording_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(auth_service.get_current_user),
):
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
