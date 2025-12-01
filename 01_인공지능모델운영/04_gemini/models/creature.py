from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class CreatureBase(BaseModel):
    name: str
    habitat: Optional[str] = None
    description: Optional[str] = None


class CreatureCreate(CreatureBase):
    pass


class CreatureGet(CreatureBase):
    id: int

    class Config:
        orm_mode = True
