from typing import Optional

from sqlmodel import SQLModel

from .base import PublicBase


class ProblemBase(SQLModel):
    question: str
    answer: str
    llm_answer: str
    steps: list[str]
    num_steps: int
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    llm_name: Optional[str] = None
    prompt_format: Optional[str] = None
    final_answer: Optional[dict] = None
    extra_metadata: Optional[dict] = None


class ProblemCreate(ProblemBase):
    pass


class ProblemPublic(ProblemBase, PublicBase):
    dataset_id: int


class ProblemUpdate(SQLModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    llm_answer: Optional[str] = None
    steps: Optional[list[str]] = None
    num_steps: Optional[int] = None
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    llm_name: Optional[str] = None
    prompt_format: Optional[str] = None
    final_answer: Optional[dict] = None
    extra_metadata: Optional[dict] = None
