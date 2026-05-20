from typing import Optional

from pydantic import BaseModel, ConfigDict


class CameraBase(BaseModel):
    name: str
    rtsp_url: str


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    status: Optional[str] = None


class CameraOut(CameraBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: Optional[str] = None
