from typing import Optional

from app.schemas.base import CreateBase, PublicBase, UpdateBase
from sqlmodel import SQLModel


class IssueBase(SQLModel):
    text: str
    resolved: bool = False


class IssueCreate(IssueBase, CreateBase):
    problem_id: int


class IssuePublic(IssueBase, PublicBase):
    problem_id: int


class IssueUpdate(UpdateBase):
    text: Optional[str] = None
    resolved: Optional[bool] = None
