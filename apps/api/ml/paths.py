"""
Central path resolution for the ML pipeline.

Every pipeline script previously computed its own paths, and three of them
got it wrong (`parents[1]` pointed inside `apps/api/ml`; `train_popularity.py`
used the absolute POSIX path `/data/processed`). This module is the single
source of truth.

Two layouts must both work:

  Repository layout (local development, CI):
      <root>/apps/api/ml/paths.py
      <root>/data/...
      <root>/apps/api/ml/artifacts/...

  Container layout (the API image):
      /app/ml/paths.py          <- `COPY apps/api /app`
      /data/...                 <- data volume
      /app/ml/artifacts/...     <- ml_artifacts volume

Artifacts and models always live beside this file, so those two are derived
from the module location and are correct in both layouts. Only the repository
root (and therefore `data/`) needs layout detection.

Resolution order for the repository root:
  1. `PROJECT_ROOT` environment variable, when set (explicit override).
  2. The nearest ancestor containing both `apps/` and `data/` (repo layout).
  3. `<ml>/../..` when it holds a `data/` directory (repo layout fallback).
  4. The filesystem root, i.e. the container layout, where data is at `/data`.
"""

import os
from pathlib import Path

__all__ = [
    "PROJECT_ROOT",
    "ML_DIR",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "INTEGRATED_DIR",
    "ARTIFACT_DIR",
    "MODEL_DIR",
    "REPORTS_DIR",
    "ensure_directories",
    "describe",
]

# Directory containing this file: <root>/apps/api/ml  or  /app/ml
ML_DIR: Path = Path(__file__).resolve().parent


def _safe_parent(path: Path, levels: int) -> Path:
    """
    Return `path` raised by `levels`, without raising IndexError.

    A shallow absolute path such as /app/ml/paths.py has only three ancestors,
    so the previous `parents[3]` raised IndexError inside the container.
    """
    current = path
    for _ in range(levels):
        if current.parent == current:
            return current
        current = current.parent
    return current


def _detect_data_dir() -> Path:
    """
    Locate the dataset root.

    `DATA_DIR` may be set explicitly; otherwise walk up looking for a real
    `data/` directory, and finally fall back to `/data` (the container mount).
    """
    override = os.getenv("DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()

    here = Path(__file__).resolve()
    for candidate in here.parents:
        data = candidate / "data"
        if data.is_dir():
            return data

    return Path("/data")


def _detect_project_root(data_dir: Path) -> Path:
    """
    Best-effort repository root, used for informational output and for
    `reports/`. Never raises.
    """
    override = os.getenv("PROJECT_ROOT")
    if override:
        candidate = Path(override).expanduser()
        if candidate.is_dir():
            return candidate.resolve()

    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "apps").is_dir() and (candidate / "data").is_dir():
            return candidate

    # Container layout: data lives at /data, so its parent is effectively root.
    if data_dir.is_dir() and data_dir.name == "data":
        return data_dir.parent

    return _safe_parent(here, 3)


DATA_DIR: Path = _detect_data_dir()
PROJECT_ROOT: Path = _detect_project_root(DATA_DIR)

# ------------------------------------------------------------
# DATA
# ------------------------------------------------------------
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
INTEGRATED_DIR: Path = PROCESSED_DATA_DIR / "integrated"

# ------------------------------------------------------------
# ML OUTPUTS
#
# Derived from the module location, so these are correct in BOTH layouts:
#   repo      -> <root>/apps/api/ml/artifacts
#   container -> /app/ml/artifacts   (where the volume is mounted)
# ------------------------------------------------------------
ARTIFACT_DIR: Path = ML_DIR / "artifacts"
MODEL_DIR: Path = ML_DIR / "models"

# ------------------------------------------------------------
# REPORTS
# ------------------------------------------------------------
REPORTS_DIR: Path = PROJECT_ROOT / "reports"


def ensure_directories() -> None:
    """Create the output directories the pipeline writes into."""
    for directory in (
        PROCESSED_DATA_DIR,
        INTEGRATED_DIR,
        ARTIFACT_DIR,
        MODEL_DIR,
        REPORTS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def describe() -> str:
    """Human-readable summary, useful for debugging path resolution."""
    lines = [
        f"ML_DIR            : {ML_DIR}",
        f"PROJECT_ROOT      : {PROJECT_ROOT}",
        f"DATA_DIR          : {DATA_DIR}",
        f"RAW_DATA_DIR      : {RAW_DATA_DIR}",
        f"PROCESSED_DATA_DIR: {PROCESSED_DATA_DIR}",
        f"INTEGRATED_DIR    : {INTEGRATED_DIR}",
        f"ARTIFACT_DIR      : {ARTIFACT_DIR}",
        f"MODEL_DIR         : {MODEL_DIR}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())