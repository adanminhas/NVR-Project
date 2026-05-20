from pathlib import Path
from subprocess import Popen, STDOUT
from typing import Dict

from app.settings import settings

# Track running ffmpeg processes in memory: {camera_id: Popen}
_processes: Dict[int, Popen] = {}


def get_stream_dir(camera_id: int) -> Path:
    camera_dir = settings.streams_dir / str(camera_id)
    camera_dir.mkdir(parents=True, exist_ok=True)
    return camera_dir


def is_stream_running(camera_id: int) -> bool:
    proc = _processes.get(camera_id)
    if not proc:
        return False

    if proc.poll() is None:
        return True

    _processes.pop(camera_id, None)
    return False


def start_stream(camera_id: int, rtsp_url: str) -> Path:
    """
    Start an ffmpeg process that pulls from the RTSP URL and writes HLS files.
    Returns the path to the HLS playlist (index.m3u8).
    """
    if camera_id in _processes:
        proc = _processes[camera_id]
        if proc.poll() is not None:
            _processes.pop(camera_id, None)

    if is_stream_running(camera_id):
        return get_stream_dir(camera_id) / "index.m3u8"

    out_dir = get_stream_dir(camera_id)
    playlist_path = out_dir / "index.m3u8"

    cmd = [
        settings.ffmpeg_path,
        "-rtsp_transport", "tcp",
        "-i", rtsp_url,
        "-c:v", "copy",
        "-c:a", "aac",
        "-f", "hls",
        "-hls_time", str(settings.hls_segment_seconds),
        "-hls_list_size", str(settings.hls_list_size),
        "-hls_flags", "delete_segments",
        str(playlist_path),
    ]

    # Capture ffmpeg output to a per-camera log so failures are diagnosable.
    log_path = out_dir / "ffmpeg.log"
    log_file = open(log_path, "a", buffering=1)
    proc = Popen(cmd, stdout=log_file, stderr=STDOUT)
    _processes[camera_id] = proc

    return playlist_path


def stop_stream(camera_id: int) -> bool:
    """Stop an ffmpeg process if tracked. Idempotent — safe to call twice."""
    proc = _processes.pop(camera_id, None)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        return True
    return False


def is_hls_active(camera_id: int) -> bool:
    stream_dir = get_stream_dir(camera_id)
    if not stream_dir.exists():
        return False
    return any(stream_dir.glob("*.ts"))
