from __future__ import annotations

import sqlite3
from typing import List, Optional

from models.creature import CreatureCreate, CreatureGet


def list_creatures(conn: sqlite3.Connection) -> List[CreatureGet]:
    rows = conn.execute(
        "SELECT id, name, habitat, description FROM creatures ORDER BY id;"
    ).fetchall()
    return [CreatureGet(**dict(row)) for row in rows]


def get_creature(conn: sqlite3.Connection, creature_id: int) -> Optional[CreatureGet]:
    row = conn.execute(
        "SELECT id, name, habitat, description FROM creatures WHERE id = ?;",
        (creature_id,),
    ).fetchone()
    return CreatureGet(**dict(row)) if row else None


def create_creature(conn: sqlite3.Connection, payload: CreatureCreate) -> CreatureGet:
    cursor = conn.execute(
        "INSERT INTO creatures (name, habitat, description) VALUES (?, ?, ?);",
        (payload.name, payload.habitat, payload.description),
    )
    conn.commit()
    creature_id = cursor.lastrowid
    return CreatureGet(id=creature_id, **payload.dict())


def update_creature(
    conn: sqlite3.Connection, creature_id: int, payload: CreatureCreate
) -> Optional[CreatureGet]:
    cursor = conn.execute(
        """
        UPDATE creatures
        SET name = ?, habitat = ?, description = ?
        WHERE id = ?;
        """,
        (payload.name, payload.habitat, payload.description, creature_id),
    )
    conn.commit()
    if cursor.rowcount == 0:
        return None
    return get_creature(conn, creature_id)


def delete_creature(conn: sqlite3.Connection, creature_id: int) -> bool:
    cursor = conn.execute("DELETE FROM creatures WHERE id = ?;", (creature_id,))
    conn.commit()
    return cursor.rowcount > 0
