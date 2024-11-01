import secrets
from datetime import datetime
from typing import Optional

from pydantic import field_validator
from sqlmodel import JSON, Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    name: str = Field(unique=True)
    api_key: str = Field(default_factory=secrets.token_urlsafe, unique=True)
    permissions: str = "standard"

    created_at: datetime = Field(default_factory=datetime.now, index=True)
    last_modified: datetime = Field(default_factory=datetime.now, index=True)

    creator_id: int = Field(foreign_key="user.id", index=True)
    modifier_id: int = Field(foreign_key="user.id", index=True)

    valid_from: datetime = Field(default_factory=datetime.now, index=True)
    valid_to: Optional[datetime] = Field(default=None, index=True)

    annotations: list["Annotation"] = Relationship(back_populates="creator")
    datasets: list["Dataset"] = Relationship(back_populates="creator")
    issues: list["Issue"] = Relationship(back_populates="creator")
    problems: list["Problem"] = Relationship(back_populates="creator")

    @field_validator("permissions")
    def validate_permissions(cls, v):
        if v not in ["standard", "admin"]:
            raise ValueError("Permissions must be either 'standard' or 'admin'")
        return v


class UserCreate(SQLModel):
    name: str


class UserPublic(UserBase):
    id: int
    created_at: datetime
    last_modified: datetime


class UserUpdate(SQLModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    permissions: Optional[str] = None

    @field_validator("permissions")
    def validate_permissions(cls, v):
        if v is not None and v not in ["standard", "admin"]:
            raise ValueError("Permissions must be either 'standard' or 'admin'")
        return v


class DatasetBase(SQLModel):
    name: str
    description: str
    domain: str  # math, coding, agentic, etc.
    extra_metadata: Optional[dict] = Field(default=None, sa_type=JSON)


class Dataset(DatasetBase, table=True):
    id: int = Field(default=None, unique=True, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_modifed: datetime = Field(default_factory=datetime.now)

    creator_id: int = Field(foreign_key="user.id")
    creator: User = Relationship(back_populates="datasets")

    valid_from: datetime = Field(default_factory=datetime.now, index=True)
    valid_to: Optional[datetime] = Field(default=None, index=True)

    problems: list["Problem"] = Relationship(
        back_populates="dataset", cascade_delete=True
    )


class DatasetCreate(DatasetBase):
    problems: list["ProblemCreate"] = []

    def to_db_model(self, creator_id: int) -> Dataset:
        return Dataset(
            name=self.name,
            description=self.description,
            domain=self.domain,
            extra_metadata=self.extra_metadata,
            creator_id=creator_id,
            problems=[
                problem.to_db_model(creator_id=creator_id) for problem in self.problems
            ],
        )


class DatasetPublic(DatasetBase):
    id: int
    created_at: datetime
    last_modified: datetime
    creator_id: int


class DatasetUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    extra_metadata: Optional[dict] = None


class ProblemBase(SQLModel):
    question: str
    answer: str
    llm_answer: str = Field(unique=True)  # LLM answers should be unique
    steps: list[str] = Field(sa_type=JSON)
    num_steps: int
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    llm_name: Optional[str] = None
    prompt_format: Optional[str] = None
    final_answer: Optional[dict] = Field(default=None, sa_type=JSON)
    extra_metadata: Optional[dict] = Field(default=None, sa_type=JSON)


class Problem(ProblemBase, table=True):
    id: int = Field(default=None, primary_key=True, unique=True)

    created_at: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)

    valid_from: datetime = Field(default_factory=datetime.now, index=True)
    valid_to: Optional[datetime] = Field(default=None, index=True)

    dataset_id: int = Field(default=None, foreign_key="dataset.id")
    dataset: Dataset = Relationship(back_populates="problems")

    annotations: list["Annotation"] = Relationship(
        back_populates="problem", cascade_delete=True
    )

    issues: list["Issue"] = Relationship(back_populates="problem", cascade_delete=True)

    creator_id: int = Field(foreign_key="user.id")
    creator: "User" = Relationship(back_populates="problems")


class ProblemCreate(ProblemBase):
    def to_db_model(self, creator_id: int) -> Problem:
        return Problem(
            question=self.question,
            answer=self.answer,
            llm_answer=self.llm_answer,
            steps=self.steps,
            num_steps=self.num_steps,
            is_correct=self.is_correct,
            solve_ratio=self.solve_ratio,
            llm_name=self.llm_name,
            prompt_format=self.prompt_format,
            final_answer=self.final_answer,
            extra_metadata=self.extra_metadata,
            creator_id=creator_id,
        )


class ProblemPublic(ProblemBase):
    id: int
    created_at: datetime
    last_modified: datetime
    dataset_id: int
    creator_id: int


class ProblemUpdate(SQLModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    llm_answer: Optional[str] = None
    steps: Optional[dict[int, str]] = None
    num_steps: Optional[int] = None
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    llm_name: Optional[str] = None
    prompt_format: Optional[str] = None
    final_answer: Optional[dict] = None
    extra_metadata: Optional[dict] = None


class AnnotationBase(SQLModel):
    step_labels: dict[int, str] = Field(default={}, sa_type=JSON)
    complete: bool = False


class Annotation(AnnotationBase, table=True):
    id: int = Field(default=None, primary_key=True, unique=True)

    created_at: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)

    # temporal tracking
    # valid_from: datetime = Field(default_factory=datetime.now, index=True)
    # valid_to: Optional[datetime] = Field(default=None, index=True)
    # modifier_id: int = Field(foreign_key="user.id", index=True)

    problem_id: int = Field(default=None, foreign_key="problem.id")
    problem: "Problem" = Relationship(back_populates="annotations")

    creator_id: int = Field(default=None, foreign_key="user.id")
    creator: "User" = Relationship(back_populates="annotations")


class AnnotationCreate(AnnotationBase):
    pass


class AnnotationPublic(AnnotationBase):
    id: int
    created_at: datetime
    last_modified: datetime
    creator_id: int


class AnnotationUpdate(SQLModel):
    step_labels: Optional[dict[int, str]] = None
    complete: Optional[bool] = None


class IssueBase(SQLModel):
    text: str
    resolved: bool = False


class Issue(IssueBase, table=True):
    id: int = Field(default=None, primary_key=True, unique=True)

    created_at: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)

    creator: "User" = Relationship(back_populates="issues")
    creator_id: int = Field(foreign_key="user.id")

    problem: "Problem" = Relationship(back_populates="issues")
    problem_id: int = Field(foreign_key="problem.id")


class IssueCreate(IssueBase):
    def to_db_model(self, creator_id: int, problem_id: int) -> Issue:
        return Issue(
            text=self.text,
            resolved=self.resolved,
            creator_id=creator_id,
            problem_id=problem_id,
        )


class IssuePublic(IssueBase):
    id: int
    creator_id: int
    problem_id: int


class IssueUpdate(SQLModel):
    text: Optional[str] = None
    resolved: Optional[bool] = None


if __name__ == "__main__":
    user = User(name="david", modifier_id=3)
    print(user)
