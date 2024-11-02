from typing import TYPE_CHECKING

from sqlmodel import JSON, Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.problem import Problem
    from app.models.user import User


class Annotation(ModelBase, table=True):
    step_labels: dict[int, str] = Field(default={}, sa_type=JSON)
    complete: bool = False

    problem_id: int = Field(default=None, foreign_key="problem.id", index=True)
    problem: "Problem" = Relationship(back_populates="annotations")

    creator: "User" = Relationship(back_populates="annotations")
