from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import JSON, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .base import ModelBase
    from .problem import Problem
    from .user import User


class Annotation(ModelBase, table=True, creator_relationship="annotations"):
    step_labels: dict[int, str] = Field(default={}, sa_type=JSON)
    complete: bool = False

    problem_id: int = Field(default=None, foreign_key="problem.id")
    problem: Problem = Relationship(back_populates="annotations")
