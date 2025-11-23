from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import STREAMS_DIR
from app.routers import cameras, streams

app = FastAPI(title="Pi NVR Backend")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount HLS static files
app.mount("/streams", StaticFiles(directory=STREAMS_DIR), name="streams")

# Include routers
app.include_router(cameras.router)
app.include_router(streams.router)

@app.get("/")
def root():
    return {"message": "Pi NVR Backend Running!"}
