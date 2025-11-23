from pathlib import Path

# Base directory = backend/ (one level above app/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Where HLS streams will be stored
STREAMS_DIR = BASE_DIR / "streams"

# Make sure the folder exists
STREAMS_DIR.mkdir(parents=True, exist_ok=True)
