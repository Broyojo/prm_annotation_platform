from typing import Optional

from sqlmodel import SQLModel

from .base import PublicBase


class IssueBase(SQLModel):
    text: str
    resolved: bool = False


class IssueCreate(IssueBase):
    problem_id: int


class IssuePublic(IssueBase, PublicBase):
    problem_id: int


class IssueUpdate(SQLModel):
    text: Optional[str] = None
    resolved: Optional[bool] = None
