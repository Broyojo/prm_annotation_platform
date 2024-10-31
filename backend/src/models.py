from datetime import datetime

from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class AnnotationBase(SQLModel):
    step_labels: dict[int, str] = Field(sa_column=Column(JSON))
    complete: bool = False


class Annotation(AnnotationBase, table=True):
    id: int = Field(nullable=False, primary_key=True, unique=True)
    created_at: datetime
    last_modified: datetime
    problem_id: int = Field(nullable=False, foreign_key="problem.id")
    problem: "Problem" = Relationship(back_populates="annotations")
    creator_id: int = Field(nullable=False, foreign_key="user.id")
    creator: "User" = Relationship(back_populates="annotations")


class AnnotationPublic(AnnotationBase):
    id: int
    created_at: datetime
    last_modified: datetime
    creator_id: int


class AnnotationCreate(AnnotationBase):
    pass


class DatasetBase(SQLModel):
    name: str
    description: str
    domain: str  # math, coding, agentic, etc.
    extra_metadata: dict | None = Field(default=None, sa_column=Column(JSON))


class Dataset(DatasetBase, table=True):
    id: int = Field(nullable=False, primary_key=True, unique=True)
    created_at: datetime
    last_modified: datetime
    creator_id: int = Field(nullable=False, foreign_key="user.id")
    creator: "User" = Relationship(back_populates="datasets")
    problems: list["Problem"] = Relationship(
        back_populates="dataset", cascade_delete=True
    )


class DatasetPublic(DatasetBase):
    id: int
    created_at: datetime
    last_modified: datetime
    creator_id: int


class DatasetCreate(DatasetBase):
    """
    Dataset creation object that users can upload when publishing a dataset.

    Along with regular fields, users can also upload problems at the same time.
    """

    problems: list["ProblemCreate"] = []


class IssueBase(SQLModel):
    text: str
    resolved: bool = False


class Issue(IssueBase, table=True):
    id: int = Field(nullable=False, primary_key=True, unique=True)
    created_at: datetime
    last_modified: datetime
    creator: "User" = Relationship(back_populates="issues")
    creator_id: int = Field(nullable=False, foreign_key="user.id")
    problem: "Problem" = Relationship(back_populates="issues")
    problem_id: int = Field(nullable=False, foreign_key="problem.id")


class IssuePublic(IssueBase):
    id: int
    creator_id: int
    problem_id: int


class IssueCreate(IssueBase):
    pass


class ProblemBase(SQLModel):
    question: str
    answer: str
    llm_answer: str = Field(unique=True)  # LLM answers should be unique
    steps: dict[int, str] = Field(sa_column=Column(JSON))
    num_steps: int
    is_correct: bool | None = None
    solve_ratio: float | None = None
    llm_name: str | None = None
    prompt_format: str | None = None
    final_answer: dict | None = Field(default=None, sa_column=Column(JSON))
    extra_metadata: dict | None = Field(default=None, sa_column=Column(JSON))


class Problem(ProblemBase, table=True):
    id: int = Field(nullable=False, primary_key=True, unique=True)
    created_at: datetime
    last_modified: datetime
    dataset_id: int = Field(nullable=False, foreign_key="dataset.id")
    dataset: Dataset = Relationship(back_populates="problems")
    annotations: list[Annotation] = Relationship(
        back_populates="problem", cascade_delete=True
    )
    issues: list[Issue] = Relationship(back_populates="problem", cascade_delete=True)


class ProblemPublic(ProblemBase):
    id: int
    created_at: datetime
    last_modified: datetime
    dataset_id: int


class ProblemCreate(ProblemBase):
    pass


class UserBase(SQLModel):
    name: str = Field(unique=True)
    api_key: str = Field(unique=True)
    permissions: str = "standard"  # standard/admin


class User(UserBase, table=True):
    id: int = Field(nullable=False, primary_key=True, unique=True)
    created_at: datetime
    last_modified: datetime
    annotations: list[Annotation] = Relationship(back_populates="creator")
    datasets: list[Dataset] = Relationship(back_populates="creator")
    issues: list[Issue] = Relationship(back_populates="creator")


class UserCreate(UserBase):
    pass


class UserPublic(UserBase):
    id: int
    created_at: datetime
    last_modified: datetime
