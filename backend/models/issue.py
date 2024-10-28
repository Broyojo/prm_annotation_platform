from datetime import datetime
from typing import TYPE_CHECKING

from models.problem import Problem
from models.user import User
from sqlmodel import Field, Relationship, SQLModel


class IssueBase(SQLModel):
    text: str
    resolved: bool = False
    created_at: datetime
    last_modified: datetime

    creator_id: int | None = Field(default=None, foreign_key="user.id")
    problem_id: int | None = Field(default=None, foreign_key="problem.id")


class Issue(IssueBase, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)

    creator: "User" = Relationship(back_populates="issues")
    problem: "Problem" = Relationship(back_populates="issues")


class IssuePublic(IssueBase):
    id: int


class IssueCreate(IssueBase):
    pass
