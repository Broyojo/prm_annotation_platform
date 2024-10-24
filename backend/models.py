from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str = Field(unique=True)
    api_key: str = Field(unique=True)
    permissions: str = "standard"  # standard/admin
    """
    access level:
    1. standard - can do everything other than delete (annotate, read from api, upload datasets with questions, etc)
    2. admin - can delete problems/datasets
    """
    # a user can have many annotations
    annotations: list["Annotation"] = Relationship(back_populates="user")

    # a user can upload datasets
    datasets: list["Dataset"] = Relationship(back_populates="creator")


class Annotation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    step_labels: str  # json object of step index -> label (good, neural, bad, error realization, <no selection>)

    problem_id: Optional[int] = Field(default=None, foreign_key="problem.id")
    problem: "Problem" = Relationship(back_populates="annotations")

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="annotations")


class Problem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    question: str
    answer: str
    llm_answer: str
    steps: str  # json object of step index -> step
    num_steps: int
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    llm_name: Optional[str] = None
    prompt_format: Optional[str] = None
    final_answer: Optional[str] = None  # json string of final answer
    extra_metadata: Optional[str] = None  # user-defined json

    annotations: list[Annotation] = Relationship(
        back_populates="problem", cascade_delete=True
    )
    dataset_id: Optional[int] = Field(default=None, foreign_key="dataset.id")
    dataset: "Dataset" = Relationship(back_populates="problems")


class Dataset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str
    description: str
    domain: str  # math, coding, agentic, etc.
    upload_date: datetime
    extra_metadata: Optional[str] = None  # user-defined json

    creator_id: Optional[int] = Field(default=None, foreign_key="user.id")
    creator: User = Relationship(back_populates="datasets")
    problems: list[Problem] = Relationship(
        back_populates="dataset", cascade_delete=True
    )
