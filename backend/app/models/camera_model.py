from sqlalchemy import Column, Integer, String
from app.database import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    rtsp_url = Column(String(255), nullable=False)
    status = Column(String(50))
