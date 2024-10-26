from datetime import datetime
from typing import Optional

from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str = Field(unique=True)
    api_key: str = Field(unique=True)
    permissions: str = "standard"  # standard/admin

    annotations: list["Annotation"] = Relationship(back_populates="creator")
    datasets: list["Dataset"] = Relationship(back_populates="creator")
    issues: list["Issue"] = Relationship(back_populates="creator")


class Annotation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    step_labels: str = Field(sa_column=Column(JSON))
    created_at: datetime
    last_modified: datetime
    complete: bool = False  # if all steps are labeled

    problem_id: Optional[int] = Field(default=None, foreign_key="problem.id")
    problem: "Problem" = Relationship(back_populates="annotations")

    creator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    creator: User = Relationship(back_populates="annotations")


class Issue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    text: str
    resolved: bool
    created_at: datetime
    last_modified: datetime

    creator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    creator: User = Relationship(back_populates="issues")

    problem_id: Optional[int] = Field(default=None, foreign_key="problem.id")
    problem: "Problem" = Relationship(back_populates="issues")


class Problem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    question: str
    answer: str
    llm_answer: str
    steps: str = Field(sa_column=Column(JSON))
    num_steps: int
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    llm_name: Optional[str] = None
    prompt_format: Optional[str] = None
    final_answer: Optional[str] = Field(default=None, sa_column=Column(JSON))
    extra_metadata: Optional[str] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime
    last_modified: datetime

    annotations: list[Annotation] = Relationship(
        back_populates="problem", cascade_delete=True
    )

    issues: list["Issue"] = Relationship(back_populates="problem", cascade_delete=True)

    dataset_id: Optional[int] = Field(default=None, foreign_key="dataset.id")
    dataset: "Dataset" = Relationship(back_populates="problems")


class Dataset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str
    description: str
    domain: str  # math, coding, agentic, etc.
    created_at: datetime
    last_modified: datetime
    extra_metadata: Optional[str] = Field(default=None, sa_column=Column(JSON))

    creator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    creator: User = Relationship(back_populates="datasets")

    problems: list[Problem] = Relationship(
        back_populates="dataset", cascade_delete=True
    )
