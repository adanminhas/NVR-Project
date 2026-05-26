from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


RecordingMode = Literal["off", "continuous"]


class CameraBase(BaseModel):
    name: str
    rtsp_url: str


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    status: Optional[str] = None
    recording_mode: Optional[RecordingMode] = None


class CameraOut(CameraBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: Optional[str] = None
    recording_mode: RecordingMode = "off"


class RecordingModeUpdate(BaseModel):
    mode: RecordingMode


class RecordingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    camera_id: int
    file_path: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    size_bytes: int
