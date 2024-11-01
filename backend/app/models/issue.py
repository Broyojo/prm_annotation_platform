from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .problem import Problem


class Issue(SQLModel, table=True, creator_relationship="issues"):
    text: str
    resolved: bool = False

    problem: Problem = Relationship(back_populates="issues")
    problem_id: int = Field(foreign_key="problem.id")
