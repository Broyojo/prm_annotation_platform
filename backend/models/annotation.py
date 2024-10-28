from datetime import datetime
from typing import TYPE_CHECKING

from models.problem import Problem
from models.user import User
from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class AnnotationBase(SQLModel):
    step_labels: str = Field(sa_column=Column(JSON))
    created_at: datetime
    last_modified: datetime
    complete: bool = False  # if all steps are labeled

    problem_id: int | None = Field(default=None, foreign_key="problem.id")
    creator_id: int | None = Field(default=None, foreign_key="user.id")


class Annotation(AnnotationBase, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)

    problem: Problem = Relationship(back_populates="annotations")
    creator: User = Relationship(back_populates="annotations")


class AnnotationPublic(AnnotationBase):
    id: int


class AnnotationCreate(AnnotationBase):
    pass
