"""Centralized project path management."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ProjectPaths:
    """Holds canonical filesystem locations for the project."""

    root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    data_dir: Path = field(init=False)
    raw_dir: Path = field(init=False)
    interim_dir: Path = field(init=False)
    processed_dir: Path = field(init=False)
    reports_dir: Path = field(init=False)
    figures_dir: Path = field(init=False)
    sqlite_path: Path = field(init=False)
    models_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "data_dir", self.root / "data")
        object.__setattr__(self, "raw_dir", self.data_dir / "raw")
        object.__setattr__(self, "interim_dir", self.data_dir / "interim")
        object.__setattr__(self, "processed_dir", self.data_dir / "processed")
        object.__setattr__(self, "reports_dir", self.root / "reports")
        object.__setattr__(self, "figures_dir", self.reports_dir / "figures")
        object.__setattr__(self, "sqlite_path", self.data_dir / "adventureworks.sqlite")
        object.__setattr__(self, "models_dir", self.root / "models")
        self._ensure_directories(
            [
                self.data_dir,
                self.raw_dir,
                self.interim_dir,
                self.processed_dir,
                self.reports_dir,
                self.figures_dir,
                self.models_dir,
            ]
        )

    @staticmethod
    def _ensure_directories(directories: Iterable[Path]) -> None:
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


PATHS = ProjectPaths()

