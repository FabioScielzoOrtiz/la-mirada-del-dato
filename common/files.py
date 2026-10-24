"""Small helpers to save and find a topic's data files.

Conventions (inside each topic folder)
- Raw files:       data/raw/<source>/<name>_<YYYY-MM-DD>.<ext>   (download date in the name, never overwritten)
- Processed files: data/processed/<name>.parquet                  (rebuilt by the processing scripts)
"""

from datetime import date
from pathlib import Path

import polars as pl
import requests

from common.paths import data_dirs


def download(url: str, topic: Path, source: str, name: str, ext: str, timeout: int = 120) -> Path:
    """Download `url` to <topic>/data/raw/<source>/<name>_<today>.<ext> and return the path."""
    raw, _ = data_dirs(topic)
    out = raw / source / f"{name}_{date.today().isoformat()}.{ext}"
    out.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    out.write_bytes(r.content)
    print(f"Saved {out.relative_to(topic)} ({len(r.content) / 1e6:.1f} MB)")
    return out


def latest_raw(topic: Path, source: str, name: str) -> Path:
    """Most recent raw file <topic>/data/raw/<source>/<name>_*.* (ISO dates sort correctly)."""
    raw, _ = data_dirs(topic)
    files = sorted((raw / source).glob(f"{name}_*.*"))
    if not files:
        raise FileNotFoundError(f"No raw file for '{name}' in {raw / source}. Run the download step first.")
    return files[-1]


def write_processed(df: pl.DataFrame, topic: Path, name: str) -> Path:
    _, processed = data_dirs(topic)
    out = processed / f"{name}.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out)
    print(f"Saved {out.relative_to(topic)} ({df.height} rows)")
    return out


def read_processed(topic: Path, name: str) -> pl.DataFrame:
    return pl.read_parquet(data_dirs(topic)[1] / f"{name}.parquet")
