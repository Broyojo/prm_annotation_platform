from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import JSON, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .annotation import Annotation
    from .base import ModelBase
    from .dataset import Dataset
    from .issue import Issue
    from .user import User


class Problem(ModelBase, table=True, creator_relationship="problems"):
    question: str
    answer: str
    llm_answer: str = Field(unique=True)
    steps: list[str] = Field(sa_type=JSON)
    num_steps: int
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    llm_name: Optional[str] = None
    prompt_format: Optional[str] = None
    final_answer: Optional[dict] = Field(default=None, sa_type=JSON)
    extra_metadata: Optional[dict] = Field(default=None, sa_type=JSON)

    dataset_id: int = Field(default=None, foreign_key="dataset.id")
    dataset: Dataset = Relationship(back_populates="problems")

    annotations: list[Annotation] = Relationship(
        back_populates="problem", cascade_delete=True
    )

    issues: list[Issue] = Relationship(back_populates="problem", cascade_delete=True)
