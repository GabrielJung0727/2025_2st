"""Utilities for loading pipe-separated value files into Python data structures."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


def load_psv(path: Path) -> List[Dict[str, Any]]:
    """Read a PSV file and return a list of dictionaries.

    Missing values are converted to None so they can map cleanly to SQLite NULLs.
    """
    df = pd.read_csv(path, sep="|")
    normalized = df.where(pd.notnull(df), None)
    return normalized.to_dict(orient="records")


def load_initial_data(base_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load both creatures and explorers datasets from the data directory."""
    creatures = load_psv(base_dir / "creatures.psv")
    explorers = load_psv(base_dir / "explorers.psv")
    return {"creatures": creatures, "explorers": explorers}
