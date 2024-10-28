from datetime import datetime
from typing import TYPE_CHECKING

from models.dataset import DatasetPublic
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .annotation import Annotation, AnnotationPublic
    from .dataset import Dataset
    from .issue import Issue, IssuePublic


class UserBase(SQLModel):
    name: str = Field(unique=True)
    api_key: str = Field(unique=True)
    permissions: str = "standard"  # standard/admin


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)

    annotations: list[Annotation] = Relationship(back_populates="creator")
    datasets: list[Dataset] = Relationship(back_populates="creator")
    issues: list[Issue] = Relationship(back_populates="creator")


class UserCreate(UserBase):
    pass


class UserPublic(UserBase):
    id: int
    annotations: list[AnnotationPublic]
    issues: list[IssuePublic]
    datasets: list[DatasetPublic]
