"""Small helpers to save and find data files.

Conventions
-----------
- Raw files:       data/raw/<source>/<name>_<YYYY-MM-DD>.<ext>   (download date in the name, never overwritten)
- Processed files: data/processed/<name>.parquet                  (rebuilt by the processing scripts)
"""

from datetime import date
from pathlib import Path

import polars as pl
import requests

from src.utils.paths import PROCESSED, RAW


def download(url: str, source: str, name: str, ext: str, timeout: int = 120) -> Path:
    """Download `url` to data/raw/<source>/<name>_<today>.<ext> and return the path."""
    out = RAW / source / f"{name}_{date.today().isoformat()}.{ext}"
    out.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    out.write_bytes(r.content)
    print(f"Saved {out.relative_to(RAW.parent.parent)} ({len(r.content) / 1e6:.1f} MB)")
    return out


def latest_raw(source: str, name: str) -> Path:
    """Most recent raw file data/raw/<source>/<name>_*.* (dates in ISO format sort correctly)."""
    files = sorted((RAW / source).glob(f"{name}_*.*"))
    if not files:
        raise FileNotFoundError(f"No raw file for '{name}' in data/raw/{source}/. Run the download step first.")
    return files[-1]


def write_processed(df: pl.DataFrame, name: str) -> Path:
    out = PROCESSED / f"{name}.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out)
    print(f"Saved data/processed/{name}.parquet ({df.height} rows)")
    return out


def read_processed(name: str) -> pl.DataFrame:
    return pl.read_parquet(PROCESSED / f"{name}.parquet")
