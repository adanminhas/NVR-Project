"""
Test fixtures.

These set up an isolated SQLite-backed test environment with subprocess.Popen
patched, so tests never spawn real ffmpeg and never touch the dev database.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Environment must be configured before any app modules import, since
# pydantic-settings reads .env at import time.
TEMP_DIR = Path(tempfile.mkdtemp(prefix="pi-nvr-tests-"))
os.environ.update(
    {
        "DATABASE_URL": f"sqlite:///{TEMP_DIR / 'test.db'}",
        "STREAMS_DIR": str(TEMP_DIR / "streams"),
        "RECORDINGS_DIR": str(TEMP_DIR / "recordings"),
        "ALLOWED_ORIGINS": "http://test",
        "ADMIN_USERNAME": "admin",
        "ADMIN_PASSWORD": "admin",
        "SECRET_KEY": "test-secret",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
        "MAX_CONCURRENT_STREAMS": "2",
    }
)


def _make_fake_proc():
    proc = MagicMock(name="FakeFFmpeg")
    proc.poll.return_value = None  # "alive"
    proc.wait.return_value = 0
    proc.terminate.return_value = None
    proc.kill.return_value = None
    return proc


# Start patches before importing the app so lifespan startup uses fake Popen.
_popen_patches = [
    patch("app.services.stream_service.Popen", side_effect=lambda *a, **kw: _make_fake_proc()),
    patch(
        "app.services.recording_service.Popen",
        side_effect=lambda *a, **kw: _make_fake_proc(),
    ),
]
for _p in _popen_patches:
    _p.start()


import pytest  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models.camera_model import Camera  # noqa: E402
from app.models.recording_model import Recording  # noqa: E402
from app.models.user_model import User  # noqa: E402
from app.services import (  # noqa: E402
    auth_service,  # noqa: E402
    recording_service,
    stream_service,
)
from app.settings import settings  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _reset_state():
    """Wipe rows and in-memory process maps between tests."""
    db = SessionLocal()
    try:
        db.query(Recording).delete()
        db.query(Camera).delete()
        db.query(User).filter(User.username != settings.admin_username).delete()
        # Make sure the bootstrap admin always exists.
        admin = db.query(User).filter(User.username == settings.admin_username).first()
        if not admin:
            admin = User(
                username=settings.admin_username,
                password_hash=auth_service.hash_password(settings.admin_password),
                is_admin=True,
            )
            db.add(admin)
        else:
            admin.is_admin = True
            admin.password_hash = auth_service.hash_password(settings.admin_password)
        db.commit()
    finally:
        db.close()

    stream_service._processes.clear()
    recording_service._recording_processes.clear()
    yield


@pytest.fixture
def admin_token(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def make_camera(client, auth_headers):
    def _make(name="Test Camera", rtsp_url="rtsp://user:pass@example.com/stream"):
        res = client.post(
            "/api/cameras/",
            headers=auth_headers,
            json={"name": name, "rtsp_url": rtsp_url},
        )
        assert res.status_code == 201, res.text
        return res.json()

    return _make
