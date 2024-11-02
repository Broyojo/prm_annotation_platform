from typing import TYPE_CHECKING

from app.models.base import ModelBase
from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from app.models.problem import Problem
    from app.models.user import User


class Issue(ModelBase, table=True):
    text: str
    resolved: bool = False

    problem: "Problem" = Relationship(back_populates="issues")
    problem_id: int = Field(foreign_key="problem.id", index=True)

    creator: "User" = Relationship(back_populates="issues")
