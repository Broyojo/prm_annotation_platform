from typing import Optional

from sqlmodel import SQLModel

from app.schemas.base import ReadBase, UpdateBase


class IssueBase(SQLModel):
    text: str
    resolved: bool = False


class IssueCreate(IssueBase):
    problem_id: int


class IssueRead(IssueBase, ReadBase):
    problem_id: int


class IssueUpdate(UpdateBase):
    text: Optional[str] = None
    resolved: Optional[bool] = None
