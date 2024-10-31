from datetime import datetime

from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class AnnotationBase(SQLModel):
    step_labels: str = Field(sa_column=Column(JSON))
    complete: bool = False  # if all steps are labeled

    problem_id: int | None = Field(default=None, foreign_key="problem.id")
    creator_id: int | None = Field(default=None, foreign_key="user.id")


class Annotation(AnnotationBase, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)
    created_at: datetime
    last_modified: datetime

    problem: "Problem" = Relationship(back_populates="annotations")
    creator: "User" = Relationship(back_populates="annotations")


class AnnotationPublic(AnnotationBase):
    id: int


class AnnotationCreate(AnnotationBase):
    pass


class DatasetBase(SQLModel):
    name: str
    description: str
    domain: str  # math, coding, agentic, etc.
    extra_metadata: str | None = Field(default=None, sa_column=Column(JSON))

    creator_id: int | None = Field(default=None, foreign_key="user.id")


class Dataset(DatasetBase, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)
    created_at: datetime
    last_modified: datetime

    creator: "User" = Relationship(back_populates="datasets")
    problems: list["Problem"] = Relationship(
        back_populates="dataset", cascade_delete=True
    )


class DatasetPublic(DatasetBase):
    id: int
    created_at: datetime
    last_modified: datetime
    creator: "User"


class DatasetCreate(DatasetBase):
    """
    Dataset creation object that users can upload when publishing a dataset.

    Along with regular fields, users can also upload problems at the same time.
    """

    problems: list["ProblemCreate"] | None


class IssueBase(SQLModel):
    text: str
    resolved: bool = False

    creator_id: int | None = Field(default=None, foreign_key="user.id")
    problem_id: int | None = Field(default=None, foreign_key="problem.id")


class Issue(IssueBase, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)
    created_at: datetime
    last_modified: datetime

    creator: "User" = Relationship(back_populates="issues")
    problem: "Problem" = Relationship(back_populates="issues")


class IssuePublic(IssueBase):
    id: int


class IssueCreate(IssueBase):
    pass


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


class UserBase(SQLModel):
    name: str = Field(unique=True)
    api_key: str = Field(unique=True)
    permissions: str = "standard"  # standard/admin


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True, unique=True)

    annotations: list[Annotation] = Relationship(back_populates="creator")
    datasets: list[Dataset] = Relationship(back_populates="creator")
    issues: list[Issue] = Relationship(back_populates="creator")


class UserCreate(UserBase):
    pass


class UserPublic(UserBase):
    id: int
    annotations: list[AnnotationPublic]
    issues: list[IssuePublic]
    datasets: list[DatasetPublic]
