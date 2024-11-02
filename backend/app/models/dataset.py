from typing import TYPE_CHECKING, Optional

from sqlmodel import JSON, Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.problem import Problem
    from app.models.user import User


class Dataset(ModelBase, table=True):
    name: str
    description: str
    domain: str  # math, coding, agentic, etc.
    extra_metadata: Optional[dict] = Field(default=None, sa_type=JSON)

    problems: list["Problem"] = Relationship(
        back_populates="dataset", cascade_delete=True
    )

    creator: "User" = Relationship(back_populates="datasets")
