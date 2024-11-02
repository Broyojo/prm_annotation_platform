from typing import Optional

from sqlmodel import SQLModel

from app.schemas.base import ReadBase, UpdateBase
from app.schemas.problem import ProblemCreate


class DatasetBase(SQLModel):
    name: str
    description: str
    domain: str
    extra_metadata: Optional[dict] = None


class DatasetCreate(DatasetBase):
    problems: list[ProblemCreate]


class DatasetRead(DatasetBase, ReadBase):
    pass


class DatasetUpdate(UpdateBase):
    name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    extra_metadata: Optional[dict] = None
