from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class UserBase(SQLModel):
    name: str = Field(unique=True)
    api_key: str = Field(unique=True)
    permissions: str = "standard"  # standard/admin


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)

    annotations: List["Annotation"] = Relationship(back_populates="creator")
    datasets: List["Dataset"] = Relationship(back_populates="creator")
    issues: List["Issue"] = Relationship(back_populates="creator")


class UserPublic(UserBase):
    id: int
    annotations: list["AnnotationPublic"]
    issues: list["IssuePublic"]


class AnnotationBase(SQLModel):
    step_labels: str = Field(sa_column=Column(JSON))
    created_at: datetime
    last_modified: datetime
    complete: bool = False  # if all steps are labeled

    problem_id: Optional[int] = Field(default=None, foreign_key="problem.id")
    creator_id: Optional[int] = Field(default=None, foreign_key="user.id")


class Annotation(AnnotationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)

    problem: "Problem" = Relationship(back_populates="annotations")
    creator: User = Relationship(back_populates="annotations")


class AnnotationPublic(AnnotationBase):
    id: int


class IssueBase(SQLModel):
    text: str
    resolved: bool = False
    created_at: datetime
    last_modified: datetime

    creator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    problem_id: Optional[int] = Field(default=None, foreign_key="problem.id")


class Issue(IssueBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)

    creator: User = Relationship(back_populates="issues")
    problem: "Problem" = Relationship(back_populates="issues")


class IssuePublic(IssueBase):
    id: int


class ProblemBase(SQLModel):
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

    dataset_id: Optional[int] = Field(default=None, foreign_key="dataset.id")


class Problem(ProblemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)

    annotations: List[Annotation] = Relationship(
        back_populates="problem", cascade_delete=True
    )
    issues: List["Issue"] = Relationship(back_populates="problem", cascade_delete=True)
    dataset: "Dataset" = Relationship(back_populates="problems")


class ProblemPublic(ProblemBase):
    id: int
    annotations: list[AnnotationPublic]
    issues: list[IssuePublic]


class DatasetBase(SQLModel):
    name: str
    description: str
    domain: str  # math, coding, agentic, etc.
    created_at: datetime
    last_modified: datetime
    extra_metadata: Optional[str] = Field(default=None, sa_column=Column(JSON))

    creator_id: Optional[int] = Field(default=None, foreign_key="user.id")


class Dataset(DatasetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)

    creator: User = Relationship(back_populates="datasets")
    problems: List[Problem] = Relationship(
        back_populates="dataset", cascade_delete=True
    )


class DatasetPublic(DatasetBase):
    id: int
