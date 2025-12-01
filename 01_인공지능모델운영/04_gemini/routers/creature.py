from __future__ import annotations

import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status

from data.database import get_db_connection
from models.creature import CreatureCreate, CreatureGet
from services import creature_service

router = APIRouter(prefix="/creatures", tags=["creatures"])


@router.get("/", response_model=List[CreatureGet])
def list_creatures(conn=Depends(get_db_connection)) -> List[CreatureGet]:
    return creature_service.list_creatures(conn)


@router.get("/{creature_id}", response_model=CreatureGet)
def read_creature(creature_id: int, conn=Depends(get_db_connection)) -> CreatureGet:
    creature = creature_service.get_creature(conn, creature_id)
    if creature is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creature not found")
    return creature


@router.post("/", response_model=CreatureGet, status_code=status.HTTP_201_CREATED)
def create_creature(payload: CreatureCreate, conn=Depends(get_db_connection)) -> CreatureGet:
    try:
        return creature_service.create_creature(conn, payload)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{creature_id}", response_model=CreatureGet)
def update_creature(
    creature_id: int, payload: CreatureCreate, conn=Depends(get_db_connection)
) -> CreatureGet:
    updated = creature_service.update_creature(conn, creature_id, payload)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creature not found")
    return updated


@router.delete("/{creature_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_creature(creature_id: int, conn=Depends(get_db_connection)) -> Response:
    deleted = creature_service.delete_creature(conn, creature_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creature not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
