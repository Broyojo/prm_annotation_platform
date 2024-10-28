from datetime import datetime
from typing import TYPE_CHECKING

from models.problem import Problem
from models.user import User
from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class DatasetBase(SQLModel):
    name: str
    description: str
    domain: str  # math, coding, agentic, etc.
    extra_metadata: str | None = Field(default=None, sa_column=Column(JSON))

    creator_id: str | None = Field(default=None, foreign_key="user.id")


class Dataset(DatasetBase, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)
    created_at: datetime
    last_modified: datetime

    creator: "User" = Relationship(back_populates="datasets")
    problems: list["Problem"] = Relationship(
        back_populates="dataset", cascade_delete=True
    )


class DatasetPublic(DatasetBase):
    id: int
    created_at: datetime
    last_modified: datetime


class DatasetCreate(DatasetBase):
    pass
