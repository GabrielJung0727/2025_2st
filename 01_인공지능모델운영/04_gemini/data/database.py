"""SQLite database setup and connection utilities."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Generator

from .psv_loader import load_initial_data

DB_PATH = Path(__file__).resolve().parent / "app.db"


def initialize_db() -> None:
    """Create tables and seed initial data from PSV files."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS creatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                habitat TEXT,
                description TEXT
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS explorers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                specialty TEXT,
                favorite_creature TEXT,
                FOREIGN KEY(favorite_creature) REFERENCES creatures(name)
            );
            """
        )

        data_dir = Path(__file__).resolve().parent
        seeds = load_initial_data(data_dir)

        creature_count = cursor.execute("SELECT COUNT(1) FROM creatures;").fetchone()[0]
        if creature_count == 0:
            cursor.executemany(
                "INSERT INTO creatures (name, habitat, description) VALUES (?, ?, ?);",
                [
                    (item.get("name"), item.get("habitat"), item.get("description"))
                    for item in seeds.get("creatures", [])
                ],
            )

        explorer_count = cursor.execute("SELECT COUNT(1) FROM explorers;").fetchone()[0]
        if explorer_count == 0:
            cursor.executemany(
                "INSERT INTO explorers (name, specialty, favorite_creature) VALUES (?, ?, ?);",
                [
                    (
                        item.get("name"),
                        item.get("specialty"),
                        item.get("favorite_creature"),
                    )
                    for item in seeds.get("explorers", [])
                ],
            )

        conn.commit()
    finally:
        conn.close()


def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency that yields a SQLite connection and closes it after use."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
