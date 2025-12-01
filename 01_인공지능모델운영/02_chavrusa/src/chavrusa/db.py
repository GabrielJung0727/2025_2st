"""SQLite helpers for AdventureWorks data."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Generator, Iterable, Tuple

import pandas as pd

from .paths import PATHS


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(PATHS.sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()


def write_dataframe(df: pd.DataFrame, table_name: str, *, if_exists: str = "replace") -> None:
    with get_connection() as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)


def read_query(query: str, params: Iterable = ()) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def table_exists(table_name: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return cursor.fetchone() is not None

