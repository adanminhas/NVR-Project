import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from subprocess import STDOUT, Popen

from app.models.camera_model import Camera
from app.models.recording_model import Recording
from app.settings import settings
from sqlalchemy.orm import Session

# Track running recording ffmpeg processes: {camera_id: Popen}
_recording_processes: dict[int, Popen] = {}

# Filenames look like: YYYY-MM-DD_HH-MM-SS.mp4
_FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})\.mp4$")


def get_recording_dir(camera_id: int) -> Path:
    cam_dir = settings.recordings_dir / str(camera_id)
    cam_dir.mkdir(parents=True, exist_ok=True)
    return cam_dir


def is_recording(camera_id: int) -> bool:
    proc = _recording_processes.get(camera_id)
    if not proc:
        return False
    if proc.poll() is None:
        return True
    _recording_processes.pop(camera_id, None)
    return False


def start_recording(camera_id: int, rtsp_url: str) -> None:
    """Spawn an ffmpeg process that segments RTSP into MP4 files."""
    if is_recording(camera_id):
        return

    out_dir = get_recording_dir(camera_id)
    pattern = str(out_dir / "%Y-%m-%d_%H-%M-%S.mp4")
    segment_seconds = settings.recording_segment_minutes * 60

    cmd = [
        settings.ffmpeg_path,
        "-rtsp_transport",
        "tcp",
        "-stream_loop",
        "-1",
        "-fflags",
        "+genpts+discardcorrupt",
        "-i",
        rtsp_url,
        "-c",
        "copy",
        "-f",
        "segment",
        "-strftime",
        "1",
        "-segment_time",
        str(segment_seconds),
        "-reset_timestamps",
        "1",
        "-segment_format",
        "mp4",
        "-segment_format_options",
        "movflags=+faststart+frag_keyframe+empty_moov",
        pattern,
    ]

    log_path = out_dir / "ffmpeg.log"
    log_file = open(log_path, "a", buffering=1)
    proc = Popen(cmd, stdout=log_file, stderr=STDOUT)
    _recording_processes[camera_id] = proc


def stop_recording(camera_id: int) -> bool:
    proc = _recording_processes.pop(camera_id, None)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        return True
    return False


def delete_recording_dir(camera_id: int) -> None:
    stop_recording(camera_id)
    cam_dir = settings.recordings_dir / str(camera_id)
    if cam_dir.exists():
        shutil.rmtree(cam_dir, ignore_errors=True)


def _parse_started_at(name: str) -> datetime | None:
    m = _FILENAME_RE.match(name)
    if not m:
        return None
    date_part, time_part = m.groups()
    try:
        return datetime.strptime(f"{date_part}_{time_part}", "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return None


def index_recordings(db: Session) -> int:
    """
    Scan recordings dir, upsert DB rows for any new MP4 files, and update
    size/duration/ended_at for files that finished writing since last scan.
    Returns the number of new rows added.
    """
    if not settings.recordings_dir.exists():
        return 0

    added = 0
    known_paths = {row[0] for row in db.query(Recording.file_path).all()}
    existing_camera_ids = {cid for (cid,) in db.query(Camera.id).all()}

    for cam_dir in settings.recordings_dir.iterdir():
        if not cam_dir.is_dir():
            continue
        try:
            camera_id = int(cam_dir.name)
        except ValueError:
            continue
        if camera_id not in existing_camera_ids:
            # Orphaned folder (camera was deleted/reset). Skip rather than
            # trying to insert rows that would fail the foreign key.
            continue

        # Sort by name so older comes first; the latest file is the active one.
        files = sorted(cam_dir.glob("*.mp4"), key=lambda p: p.name)
        for idx, file_path in enumerate(files):
            started_at = _parse_started_at(file_path.name)
            if not started_at:
                continue

            try:
                stat = file_path.stat()
            except FileNotFoundError:
                continue

            is_latest = idx == len(files) - 1
            ended_at = None
            duration = None
            if not is_latest:
                # Older files are finalized — derive duration from next start.
                next_started = _parse_started_at(files[idx + 1].name)
                if next_started:
                    ended_at = next_started
                    duration = int((next_started - started_at).total_seconds())
            elif not is_recording(camera_id):
                # Newest file but ffmpeg isn't writing anymore — finalize it
                # using the file's last-modified time.
                ended_at = datetime.fromtimestamp(stat.st_mtime)
                duration = max(0, int((ended_at - started_at).total_seconds()))

            path_str = str(file_path)
            existing = db.query(Recording).filter(Recording.file_path == path_str).first()
            if existing:
                existing.size_bytes = stat.st_size
                if ended_at and not existing.ended_at:
                    existing.ended_at = ended_at
                    existing.duration_seconds = duration
                continue

            if path_str not in known_paths:
                db.add(
                    Recording(
                        camera_id=camera_id,
                        file_path=path_str,
                        started_at=started_at,
                        ended_at=ended_at,
                        duration_seconds=duration,
                        size_bytes=stat.st_size,
                    )
                )
                added += 1

    db.commit()
    return added


def list_recordings(
    db: Session,
    camera_id: int | None = None,
    start_from: datetime | None = None,
    start_to: datetime | None = None,
) -> list[Recording]:
    index_recordings(db)
    q = db.query(Recording)
    if camera_id is not None:
        q = q.filter(Recording.camera_id == camera_id)
    if start_from is not None:
        q = q.filter(Recording.started_at >= start_from)
    if start_to is not None:
        q = q.filter(Recording.started_at < start_to)
    return q.order_by(Recording.started_at.desc()).all()


def sweep_retention(db: Session) -> int:
    """Delete recordings older than RETENTION_DAYS, from both disk and DB."""
    if settings.retention_days <= 0:
        return 0

    cutoff = datetime.utcnow() - timedelta(days=settings.retention_days)
    old = db.query(Recording).filter(Recording.started_at < cutoff).all()
    deleted = 0
    for rec in old:
        try:
            Path(rec.file_path).unlink(missing_ok=True)
        except OSError:
            pass
        db.delete(rec)
        deleted += 1
    db.commit()
    return deleted
