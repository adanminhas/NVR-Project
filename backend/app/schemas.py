from datetime import datetime
from typing import Literal, Optional
from urllib.parse import urlparse, urlunparse

from pydantic import BaseModel, ConfigDict, field_serializer


MASKED_CREDS = "***:***"


def mask_rtsp_credentials(url: str) -> str:
    """Replace user:pass in an RTSP URL with ***:*** for display."""
    if not url or "@" not in url:
        return url
    try:
        parsed = urlparse(url)
    except ValueError:
        return url
    if not parsed.username and not parsed.password:
        return url
    netloc = parsed.hostname or ""
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    netloc = f"{MASKED_CREDS}@{netloc}"
    return urlunparse(parsed._replace(netloc=netloc))


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

    @field_serializer("rtsp_url")
    def _mask_rtsp(self, value: str) -> str:
        return mask_rtsp_credentials(value)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_admin: bool = False


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class PasswordChange(BaseModel):
    password: str


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
