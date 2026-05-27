from app.services import stream_service


def test_start_stream_spawns_ffmpeg(client, auth_headers, make_camera):
    cam = make_camera()
    res = client.post(f"/api/streams/{cam['id']}/start", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "streaming"
    assert cam["id"] in stream_service._processes


def test_stop_stream_terminates_ffmpeg(client, auth_headers, make_camera):
    cam = make_camera()
    client.post(f"/api/streams/{cam['id']}/start", headers=auth_headers)
    proc = stream_service._processes[cam["id"]]

    res = client.post(f"/api/streams/{cam['id']}/stop", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "stopped"
    proc.terminate.assert_called_once()
    assert cam["id"] not in stream_service._processes


def test_stop_is_idempotent(client, auth_headers, make_camera):
    cam = make_camera()
    # No prior start.
    res = client.post(f"/api/streams/{cam['id']}/stop", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "stopped"
    assert "not running" in res.json()["message"].lower()


def test_health_endpoint_shape(client, auth_headers, make_camera):
    cam = make_camera()
    res = client.get(f"/api/streams/{cam['id']}/health", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    for key in (
        "camera_id",
        "ffmpeg_running",
        "playlist_exists",
        "playlist_age_seconds",
        "last_segment_age_seconds",
        "is_live",
        "recent_log_lines",
    ):
        assert key in body
    assert body["ffmpeg_running"] is False
    assert body["is_live"] is False


def test_concurrency_cap_returns_429(client, auth_headers, make_camera):
    # MAX_CONCURRENT_STREAMS=2 in tests
    c1 = make_camera(name="cam1")
    c2 = make_camera(name="cam2")
    c3 = make_camera(name="cam3")
    assert client.post(f"/api/streams/{c1['id']}/start", headers=auth_headers).status_code == 200
    assert client.post(f"/api/streams/{c2['id']}/start", headers=auth_headers).status_code == 200
    res = client.post(f"/api/streams/{c3['id']}/start", headers=auth_headers)
    assert res.status_code == 429
