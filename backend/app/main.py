from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import cameras, streams
from app.settings import settings

app = FastAPI(title="Pi NVR Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/streams", StaticFiles(directory=settings.streams_dir), name="streams")

app.include_router(cameras.router)
app.include_router(streams.router)


@app.get("/")
def root():
    return {"message": "Pi NVR Backend Running!"}
