from typing import Optional

from sqlmodel import SQLModel

from .base import PublicBase


class AnnotationBase(SQLModel):
    step_labels: dict[int, str] = {}
    complete: bool = False


class AnnotationCreate(AnnotationBase):
    problem_id: int


class AnnotationPublic(AnnotationBase, PublicBase):
    problem_id: int


class AnnotationUpdate(SQLModel):
    step_labels: Optional[dict[int, str]] = None
    complete: Optional[bool] = None
