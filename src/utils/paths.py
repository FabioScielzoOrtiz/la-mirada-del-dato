"""Project paths. Everything is relative to the project root, wherever the code is run from."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]        # src/utils/paths.py -> project root
DATA = ROOT / "data"
RAW = DATA / "raw"                                # original downloads, never edited
PROCESSED = DATA / "processed"                    # clean tables (Parquet) read by notebooks and posts
