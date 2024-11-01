from typing import TYPE_CHECKING, Optional

from sqlmodel import JSON, Field, Relationship

if TYPE_CHECKING:
    from app.models.annotation import Annotation
    from app.models.base import ModelBase
    from app.models.dataset import Dataset
    from app.models.issue import Issue
    from app.models.user import User


class Problem(ModelBase, table=True):
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

    dataset_id: int = Field(default=None, foreign_key="dataset.id", index=True)
    dataset: Dataset = Relationship(back_populates="problems")

    annotations: list[Annotation] = Relationship(
        back_populates="problem", cascade_delete=True
    )

    issues: list[Issue] = Relationship(back_populates="problem", cascade_delete=True)

    creator: "User" = Relationship(back_populates="problems")
