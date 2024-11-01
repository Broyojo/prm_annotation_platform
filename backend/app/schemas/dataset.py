from typing import Optional

from app.schemas.base import CreateBase, PublicBase, UpdateBase
from app.schemas.problem import ProblemCreate
from sqlmodel import SQLModel


class DatasetBase(SQLModel):
    name: str
    description: str
    domain: str
    extra_metadata: Optional[dict] = None


class DatasetCreate(DatasetBase, CreateBase):
    problems: list[ProblemCreate]


class DatasetPublic(DatasetBase, PublicBase):
    pass


class DatasetUpdate(UpdateBase):
    name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    extra_metadata: Optional[dict] = None
