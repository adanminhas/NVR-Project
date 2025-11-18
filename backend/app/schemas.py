from typing import Optional
from pydantic import BaseModel

# Shared fields between read and write
class CameraBase(BaseModel):
    name: str
    rtsp_url: str


# Used when creating a camera (client -> API)
class CameraCreate(CameraBase):
    pass


# Used when updating a camera (client -> API)
class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    status: Optional[str] = None


# Used when returning a camera (API -> client)
class CameraOut(CameraBase):
    id: int
    status: Optional[str] = None

    class Config:
        orm_mode = True  # important: allows returning SQLAlchemy models
