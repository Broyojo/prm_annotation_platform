from typing import Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str = Field(unique=True)
    api_key: str = Field(unique=True)
    permissions: str = "standard"
    """
    access level:
    1. standard - can do everything other than delete (annotate, read from api, upload datasets with questions, etc)
    2. admin - can delete problems/datasets
    """

    # a user can have many annotations
    annotations: list["Annotation"] = Relationship(back_populates="user")


class Annotation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    step_labels: str  # json list of label per step

    problem: "Problem" = Relationship(back_populates="annotations")
    user: User = Relationship(back_populates="annotations")


class Problem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    question: str
    answer: str
    model_answer: str
    steps: str  # json list of steps
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    model_name: Optional[str] = None
    prompt_format: Optional[str] = None
    final_answer: Optional[str] = None  # json string of final answer

    annotations: list[Annotation] = Relationship(
        back_populates="problem", cascade_delete=True
    )
    dataset: "Dataset" = Relationship(back_populates="problems")


class Dataset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str
    domain: str  # math, coding, agentic, etc.

    problems: list[Problem] = Relationship(
        back_populates="dataset", cascade_delete=True
    )


if __name__ == "__main__":
    pass
