import secrets
from typing import TYPE_CHECKING

from pydantic import field_validator
from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .annotation import Annotation
    from .base import ModelBase
    from .dataset import Dataset
    from .issue import Issue
    from .problem import Problem


class User(ModelBase, table=True, creator_relationship="users"):
    name: str = Field(unique=True)
    api_key: str = Field(default_factory=secrets.token_urlsafe, unique=True)
    permissions: str = "standard"

    users: list["User"] = Relationship(back_populates="creator")
    annotations: list[Annotation] = Relationship(back_populates="creator")
    datasets: list[Dataset] = Relationship(back_populates="creator")
    issues: list[Issue] = Relationship(back_populates="creator")
    problems: list[Problem] = Relationship(back_populates="creator")

    @field_validator("permissions")
    def validate_permissions(cls, v):
        if v not in ["standard", "admin"]:
            raise ValueError("Permissions must be either 'standard' or 'admin'")
        return v
