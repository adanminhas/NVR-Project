from app.database import SessionLocal
from app.models.recording_model import Recording
from app.settings import settings


def test_list_empty(client, auth_headers, make_camera):
    make_camera()
    res = client.get("/api/recordings/", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


def test_indexer_skips_orphan_dirs(client, auth_headers):
    # Create an orphan recording folder for a camera that doesn't exist.
    orphan = settings.recordings_dir / "999"
    orphan.mkdir(parents=True, exist_ok=True)
    (orphan / "2026-05-26_10-00-00.mp4").write_bytes(b"fake video data")

    res = client.get("/api/recordings/", headers=auth_headers)
    assert res.status_code == 200
    # Indexer must not blow up and must not create a row for the orphan.
    assert res.json() == []


def test_indexer_picks_up_real_files(client, auth_headers, make_camera):
    cam = make_camera()
    cam_dir = settings.recordings_dir / str(cam["id"])
    cam_dir.mkdir(parents=True, exist_ok=True)
    f1 = cam_dir / "2026-05-26_10-00-00.mp4"
    f2 = cam_dir / "2026-05-26_10-10-00.mp4"
    f1.write_bytes(b"first")
    f2.write_bytes(b"second segment")

    res = client.get("/api/recordings/", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 2

    # Newest first
    assert body[0]["file_path"].endswith("2026-05-26_10-10-00.mp4")
    # Older file has a duration derived from the newer file's start.
    older = next(r for r in body if r["file_path"].endswith("2026-05-26_10-00-00.mp4"))
    assert older["duration_seconds"] == 600


def test_delete_removes_file_and_row(client, auth_headers, make_camera):
    cam = make_camera()
    cam_dir = settings.recordings_dir / str(cam["id"])
    cam_dir.mkdir(parents=True, exist_ok=True)
    f = cam_dir / "2026-05-26_11-00-00.mp4"
    f.write_bytes(b"data")

    listing = client.get("/api/recordings/", headers=auth_headers).json()
    rec_id = listing[0]["id"]

    res = client.delete(f"/api/recordings/{rec_id}", headers=auth_headers)
    assert res.status_code == 204
    assert not f.exists()

    db = SessionLocal()
    try:
        assert db.query(Recording).filter(Recording.id == rec_id).first() is None
    finally:
        db.close()


def test_file_endpoint_requires_token_param(client, auth_headers, make_camera):
    cam = make_camera()
    cam_dir = settings.recordings_dir / str(cam["id"])
    cam_dir.mkdir(parents=True, exist_ok=True)
    f = cam_dir / "2026-05-26_12-00-00.mp4"
    f.write_bytes(b"data")
    rec_id = client.get("/api/recordings/", headers=auth_headers).json()[0]["id"]

    # Without ?token, fails as 422 (missing required query param).
    res = client.get(f"/api/recordings/{rec_id}/file")
    assert res.status_code == 422

    # With bad token, fails as 401.
    res = client.get(f"/api/recordings/{rec_id}/file?token=garbage")
    assert res.status_code == 401


def test_file_endpoint_accepts_valid_query_token(client, auth_headers, admin_token, make_camera):
    cam = make_camera()
    cam_dir = settings.recordings_dir / str(cam["id"])
    cam_dir.mkdir(parents=True, exist_ok=True)
    f = cam_dir / "2026-05-26_13-00-00.mp4"
    f.write_bytes(b"hello world video")
    rec_id = client.get("/api/recordings/", headers=auth_headers).json()[0]["id"]

    res = client.get(f"/api/recordings/{rec_id}/file?token={admin_token}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "video/mp4"
    assert res.content == b"hello world video"
