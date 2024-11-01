from typing import TYPE_CHECKING, Optional

from sqlmodel import JSON, Field, Relationship

if TYPE_CHECKING:
    from .base import ModelBase
    from .problem import Problem


class Dataset(ModelBase, table=True, creator_relationship="datasets"):
    name: str
    description: str
    domain: str  # math, coding, agentic, etc.
    extra_metadata: Optional[dict] = Field(default=None, sa_type=JSON)

    problems: list[Problem] = Relationship(
        back_populates="dataset", cascade_delete=True
    )
