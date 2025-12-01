from __future__ import annotations

import sqlite3
from typing import List, Optional

from models.explorer import ExplorerCreate, ExplorerGet


def list_explorers(conn: sqlite3.Connection) -> List[ExplorerGet]:
    rows = conn.execute(
        "SELECT id, name, specialty, favorite_creature FROM explorers ORDER BY id;"
    ).fetchall()
    return [ExplorerGet(**dict(row)) for row in rows]


def get_explorer(conn: sqlite3.Connection, explorer_id: int) -> Optional[ExplorerGet]:
    row = conn.execute(
        "SELECT id, name, specialty, favorite_creature FROM explorers WHERE id = ?;",
        (explorer_id,),
    ).fetchone()
    return ExplorerGet(**dict(row)) if row else None


def create_explorer(conn: sqlite3.Connection, payload: ExplorerCreate) -> ExplorerGet:
    cursor = conn.execute(
        "INSERT INTO explorers (name, specialty, favorite_creature) VALUES (?, ?, ?);",
        (payload.name, payload.specialty, payload.favorite_creature),
    )
    conn.commit()
    explorer_id = cursor.lastrowid
    return ExplorerGet(id=explorer_id, **payload.dict())


def update_explorer(
    conn: sqlite3.Connection, explorer_id: int, payload: ExplorerCreate
) -> Optional[ExplorerGet]:
    cursor = conn.execute(
        """
        UPDATE explorers
        SET name = ?, specialty = ?, favorite_creature = ?
        WHERE id = ?;
        """,
        (payload.name, payload.specialty, payload.favorite_creature, explorer_id),
    )
    conn.commit()
    if cursor.rowcount == 0:
        return None
    return get_explorer(conn, explorer_id)


def delete_explorer(conn: sqlite3.Connection, explorer_id: int) -> bool:
    cursor = conn.execute("DELETE FROM explorers WHERE id = ?;", (explorer_id,))
    conn.commit()
    return cursor.rowcount > 0
