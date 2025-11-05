from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pi NVR Backend")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Pi NVR Backend Running!"}

@app.get("/api/cameras")
def get_cameras():
    return [
        {"id": 1, "name": "Front Door", "status": "online"},
        {"id": 2, "name": "Garage", "status": "offline"},
    ]
