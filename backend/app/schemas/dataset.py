from typing import Optional

from sqlmodel import SQLModel

from .base import PublicBase
from .problem import ProblemPublic


class DatasetBase(SQLModel):
    name: str
    description: str
    domain: str
    extra_metadata: Optional[dict] = None


class DatasetCreate(DatasetBase):
    problems: list[ProblemPublic]


class DatasetPublic(DatasetBase, PublicBase):
    pass


class DatasetUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    extra_metadata: Optional[dict] = None
