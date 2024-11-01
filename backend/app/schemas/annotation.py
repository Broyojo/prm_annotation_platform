from typing import Optional

from app.schemas.base import CreateBase, PublicBase, UpdateBase
from sqlmodel import SQLModel


class AnnotationBase(SQLModel):
    step_labels: dict[int, str] = {}
    complete: bool = False


class AnnotationCreate(AnnotationBase, CreateBase):
    problem_id: int


class AnnotationPublic(AnnotationBase, PublicBase):
    problem_id: int


class AnnotationUpdate(UpdateBase):
    step_labels: Optional[dict[int, str]] = None
    complete: Optional[bool] = None
