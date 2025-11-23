from pathlib import Path
from subprocess import Popen, DEVNULL, STDOUT
from typing import Dict

from app.config import STREAMS_DIR

# Track running ffmpeg processes in memory: {camera_id: Popen}
_processes: Dict[int, Popen] = {}


def get_stream_dir(camera_id: int) -> Path:
    """
    Return the directory where this camera's HLS files will live.
    Ensures the folder exists.
    """
    camera_dir = STREAMS_DIR / str(camera_id)
    camera_dir.mkdir(parents=True, exist_ok=True)
    return camera_dir


def is_stream_running(camera_id: int) -> bool:
    """
    Check if we already have a running ffmpeg process for this camera.
    """
    proc = _processes.get(camera_id)
    return bool(proc and proc.poll() is None)


def start_stream(camera_id: int, rtsp_url: str) -> Path:
    """
    Start an ffmpeg process that pulls from the RTSP URL and writes HLS files.

    Returns the path to the HLS playlist (index.m3u8).
    """
    # If already running, just return existing playlist path
    if is_stream_running(camera_id):
        return get_stream_dir(camera_id) / "index.m3u8"

    out_dir = get_stream_dir(camera_id)
    playlist_path = out_dir / "index.m3u8"

    # Basic ffmpeg command: RTSP -> HLS
    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",   # more reliable than UDP for RTSP
        "-i", rtsp_url,             # input RTSP url
        "-c:v", "copy",             # copy video stream (no re-encode for now)
        "-c:a", "aac",              # encode audio to AAC
        "-f", "hls",                # output format: HLS
        "-hls_time", "2",           # each segment ~2 seconds
        "-hls_list_size", "5",      # keep last 5 segments in playlist
        "-hls_flags", "delete_segments",  # delete old segments to save space
        str(playlist_path),
    ]

    # Start ffmpeg as a background process, silence output for now
    proc = Popen(cmd, stdout=DEVNULL, stderr=STDOUT)
    _processes[camera_id] = proc

    return playlist_path


def stop_stream(camera_id: int) -> bool:
    """
    Stop the ffmpeg process for a given camera, if running.
    Returns True if a process was stopped.
    """
    proc = _processes.get(camera_id)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        return True
    return False
