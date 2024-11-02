from typing import Optional

from sqlmodel import SQLModel

from app.schemas.base import ReadBase, UpdateBase


class AnnotationBase(SQLModel):
    step_labels: dict[int, str] = {}
    complete: bool = False


class AnnotationCreate(AnnotationBase):
    problem_id: int


class AnnotationRead(AnnotationBase, ReadBase):
    problem_id: int


class AnnotationUpdate(UpdateBase):
    step_labels: Optional[dict[int, str]] = None
    complete: Optional[bool] = None
