"""Project paths. Each topic (poblacion/, vivienda/…) is a mini-project: <topic>/{src,data,notebooks}."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]        # common/paths.py -> repo root


def topic_dir(start=None) -> Path:
    """Topic folder that contains `start` (default: the current directory; in scripts pass __file__)."""
    here = Path(start or Path.cwd()).resolve()
    for p in [here, *here.parents]:
        if p != ROOT and (p / "notebooks").is_dir():
            return p
    raise RuntimeError(f"{here} is not inside a topic folder (one with a notebooks/ subfolder).")


def data_dirs(topic: Path) -> tuple[Path, Path]:
    """(raw, processed) folders of a topic. Raw is never edited; processed is rebuilt by the scripts."""
    return topic / "data" / "raw", topic / "data" / "processed"
