"""Utility helpers used across the project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def to_snake_case(value: str) -> str:
    """Convert camel or spaced column names to snake_case."""
    cleaned = []
    prev_lower = False
    for char in value.strip():
        if char.isupper() and prev_lower:
            cleaned.append("_")
        if not char.isalnum():
            cleaned.append("_")
        else:
            cleaned.append(char.lower())
        prev_lower = char.islower() or char.isdigit()
    collapsed = "".join(cleaned)
    while "__" in collapsed:
        collapsed = collapsed.replace("__", "_")
    return collapsed.strip("_")


def write_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".parquet":
        df.to_parquet(path, index=False)
    elif path.suffix == ".csv":
        df.to_csv(path, index=False)
    else:
        raise ValueError(f"Unsupported file extension for {path}")

