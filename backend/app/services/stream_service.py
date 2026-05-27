import shutil
import time
from pathlib import Path
from subprocess import STDOUT, Popen

from app.settings import settings

# Track running ffmpeg processes in memory: {camera_id: Popen}
_processes: dict[int, Popen] = {}


class StreamLimitExceeded(Exception):
    """Raised when starting a stream would exceed max_concurrent_streams."""


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


def _running_count() -> int:
    return sum(1 for cid in list(_processes) if is_stream_running(cid))


def _cleanup_segments(camera_id: int) -> None:
    """Remove stale .ts and .m3u8 files but keep ffmpeg.log for history."""
    stream_dir = settings.streams_dir / str(camera_id)
    if not stream_dir.exists():
        return
    for f in stream_dir.iterdir():
        if f.suffix in {".ts", ".m3u8"}:
            try:
                f.unlink()
            except OSError:
                pass


def delete_stream_dir(camera_id: int) -> None:
    """Stop the stream (if running) and remove the entire stream directory."""
    stop_stream(camera_id)
    stream_dir = settings.streams_dir / str(camera_id)
    if stream_dir.exists():
        shutil.rmtree(stream_dir, ignore_errors=True)


def start_stream(camera_id: int, rtsp_url: str) -> Path:
    """
    Start an ffmpeg process that pulls from the RTSP URL and writes HLS files.
    Returns the path to the HLS playlist (index.m3u8).
    Raises StreamLimitExceeded if too many streams are already running.
    """
    if camera_id in _processes:
        proc = _processes[camera_id]
        if proc.poll() is not None:
            _processes.pop(camera_id, None)

    if is_stream_running(camera_id):
        return get_stream_dir(camera_id) / "index.m3u8"

    if _running_count() >= settings.max_concurrent_streams:
        raise StreamLimitExceeded(f"Already running {settings.max_concurrent_streams} streams")

    out_dir = get_stream_dir(camera_id)
    _cleanup_segments(camera_id)
    playlist_path = out_dir / "index.m3u8"

    cmd = [
        settings.ffmpeg_path,
        "-rtsp_transport",
        "tcp",
        "-stream_loop",
        "-1",  # loop test/file sources forever; no-op for live RTSP
        "-fflags",
        "+genpts+discardcorrupt",  # clean timestamps from misbehaving sources
        "-i",
        rtsp_url,
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-f",
        "hls",
        "-hls_time",
        str(settings.hls_segment_seconds),
        "-hls_list_size",
        str(settings.hls_list_size),
        "-hls_flags",
        "delete_segments+omit_endlist",
        str(playlist_path),
    ]

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


def _file_age_seconds(path: Path) -> float | None:
    try:
        return max(0.0, time.time() - path.stat().st_mtime)
    except FileNotFoundError:
        return None


def _newest_segment(camera_id: int) -> Path | None:
    stream_dir = settings.streams_dir / str(camera_id)
    if not stream_dir.exists():
        return None
    segments = list(stream_dir.glob("*.ts"))
    if not segments:
        return None
    return max(segments, key=lambda p: p.stat().st_mtime)


def _tail_ffmpeg_log(camera_id: int, lines: int = 10) -> list[str]:
    log_path = settings.streams_dir / str(camera_id) / "ffmpeg.log"
    if not log_path.exists():
        return []
    try:
        with log_path.open("r", errors="replace") as f:
            return f.readlines()[-lines:]
    except OSError:
        return []


def get_stream_health(camera_id: int) -> dict:
    """Return a rich health snapshot for the stream."""
    stream_dir = settings.streams_dir / str(camera_id)
    playlist_path = stream_dir / "index.m3u8"
    newest_segment = _newest_segment(camera_id)

    playlist_age = _file_age_seconds(playlist_path)
    segment_age = _file_age_seconds(newest_segment) if newest_segment is not None else None

    running = is_stream_running(camera_id)
    # "live" = ffmpeg is alive AND a fresh segment landed in the last 10s
    is_live = running and segment_age is not None and segment_age < 10

    return {
        "camera_id": camera_id,
        "ffmpeg_running": running,
        "playlist_exists": playlist_path.exists(),
        "playlist_age_seconds": playlist_age,
        "last_segment_age_seconds": segment_age,
        "is_live": is_live,
        "recent_log_lines": _tail_ffmpeg_log(camera_id, lines=10),
    }


# Kept for backwards-compat with the previous health endpoint shape.
def is_hls_active(camera_id: int) -> bool:
    return _newest_segment(camera_id) is not None
