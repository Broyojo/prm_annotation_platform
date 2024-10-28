from datetime import datetime
from typing import TYPE_CHECKING

from models.annotation import Annotation, AnnotationPublic
from models.dataset import Dataset
from models.issue import Issue, IssuePublic
from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class ProblemBase(SQLModel):
    question: str
    answer: str
    llm_answer: str = Field(unique=True)  # LLM answers should be unique
    steps: str = Field(sa_column=Column(JSON))
    num_steps: int
    is_correct: bool | None = None
    solve_ratio: float | None = None
    llm_name: str | None = None
    prompt_format: str | None = None
    final_answer: str | None = Field(default=None, sa_column=Column(JSON))
    extra_metadata: str | None = Field(default=None, sa_column=Column(JSON))

    dataset_id: int | None = Field(default=None, foreign_key="dataset.id")


class Problem(ProblemBase, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)
    created_at: datetime
    last_modified: datetime

    annotations: list[Annotation] = Relationship(
        back_populates="problem", cascade_delete=True
    )
    issues: list[Issue] = Relationship(back_populates="problem", cascade_delete=True)
    dataset: Dataset = Relationship(back_populates="problems")


class ProblemPublic(ProblemBase):
    id: int
    created_at: datetime
    last_modified: datetime
    annotations: list[AnnotationPublic]
    issues: list[IssuePublic]


class ProblemCreate(ProblemBase):
    pass
