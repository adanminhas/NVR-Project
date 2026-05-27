def test_list_requires_auth(client):
    res = client.get("/api/cameras/")
    assert res.status_code == 401


def test_create_then_list(client, auth_headers):
    res = client.post(
        "/api/cameras/",
        headers=auth_headers,
        json={"name": "Front", "rtsp_url": "rtsp://user:pw@cam.example/1"},
    )
    assert res.status_code == 201
    created = res.json()
    assert created["name"] == "Front"
    assert created["status"] == "offline"
    assert created["recording_mode"] == "off"

    listing = client.get("/api/cameras/", headers=auth_headers).json()
    assert len(listing) == 1
    assert listing[0]["id"] == created["id"]


def test_rtsp_url_masked_in_response(client, auth_headers, make_camera):
    cam = make_camera(rtsp_url="rtsp://user:secret@cam.example/1")
    assert "secret" not in cam["rtsp_url"]
    assert "***:***" in cam["rtsp_url"]


def test_update_name_does_not_clobber_rtsp(client, auth_headers, make_camera):
    cam = make_camera(rtsp_url="rtsp://user:secret@cam.example/1")
    # Frontend echoes back the masked URL — backend should ignore it.
    res = client.put(
        f"/api/cameras/{cam['id']}",
        headers=auth_headers,
        json={"name": "Renamed", "rtsp_url": cam["rtsp_url"]},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "Renamed"

    # The DB should still have the original RTSP URL with creds intact.
    from app.database import SessionLocal
    from app.models.camera_model import Camera

    db = SessionLocal()
    try:
        stored = db.query(Camera).filter(Camera.id == cam["id"]).first()
        assert "secret" in stored.rtsp_url
    finally:
        db.close()


def test_update_rtsp_url_changes_value(client, auth_headers, make_camera):
    cam = make_camera()
    res = client.put(
        f"/api/cameras/{cam['id']}",
        headers=auth_headers,
        json={"rtsp_url": "rtsp://newuser:newpw@other.example/2"},
    )
    assert res.status_code == 200

    from app.database import SessionLocal
    from app.models.camera_model import Camera

    db = SessionLocal()
    try:
        stored = db.query(Camera).filter(Camera.id == cam["id"]).first()
        assert stored.rtsp_url == "rtsp://newuser:newpw@other.example/2"
    finally:
        db.close()


def test_delete_camera(client, auth_headers, make_camera):
    cam = make_camera()
    res = client.delete(f"/api/cameras/{cam['id']}", headers=auth_headers)
    assert res.status_code == 204
    listing = client.get("/api/cameras/", headers=auth_headers).json()
    assert listing == []


def test_get_404(client, auth_headers):
    res = client.get("/api/cameras/9999", headers=auth_headers)
    assert res.status_code == 404
