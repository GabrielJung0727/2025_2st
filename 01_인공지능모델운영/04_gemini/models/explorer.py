from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ExplorerBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    favorite_creature: Optional[str] = None


class ExplorerCreate(ExplorerBase):
    pass


class ExplorerGet(ExplorerBase):
    id: int

    class Config:
        orm_mode = True
