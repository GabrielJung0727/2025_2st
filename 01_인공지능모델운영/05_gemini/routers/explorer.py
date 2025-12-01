from __future__ import annotations

import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status

from data.database import get_db_connection
from models.explorer import ExplorerCreate, ExplorerGet
from services import explorer_service

router = APIRouter(prefix="/explorers", tags=["explorers"])


@router.get("/", response_model=List[ExplorerGet])
def list_explorers(conn=Depends(get_db_connection)) -> List[ExplorerGet]:
    return explorer_service.list_explorers(conn)


@router.get("/{explorer_id}", response_model=ExplorerGet)
def read_explorer(explorer_id: int, conn=Depends(get_db_connection)) -> ExplorerGet:
    explorer = explorer_service.get_explorer(conn, explorer_id)
    if explorer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explorer not found")
    return explorer


@router.post("/", response_model=ExplorerGet, status_code=status.HTTP_201_CREATED)
def create_explorer(payload: ExplorerCreate, conn=Depends(get_db_connection)) -> ExplorerGet:
    try:
        return explorer_service.create_explorer(conn, payload)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{explorer_id}", response_model=ExplorerGet)
def update_explorer(
    explorer_id: int, payload: ExplorerCreate, conn=Depends(get_db_connection)
) -> ExplorerGet:
    updated = explorer_service.update_explorer(conn, explorer_id, payload)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explorer not found")
    return updated


@router.delete("/{explorer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_explorer(explorer_id: int, conn=Depends(get_db_connection)) -> Response:
    deleted = explorer_service.delete_explorer(conn, explorer_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explorer not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
