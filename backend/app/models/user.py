import secrets
from typing import TYPE_CHECKING

from pydantic import field_validator
from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.annotation import Annotation
    from app.models.dataset import Dataset
    from app.models.issue import Issue
    from app.models.problem import Problem


class User(ModelBase, table=True, creator_relationship="users"):
    name: str = Field(unique=True)
    api_key: str = Field(default_factory=secrets.token_urlsafe, unique=True)
    permissions: str = "standard"

    users: list["User"] = Relationship(back_populates="creator")
    annotations: list["Annotation"] = Relationship(back_populates="creator")
    datasets: list["Dataset"] = Relationship(back_populates="creator")
    issues: list["Issue"] = Relationship(back_populates="creator")
    problems: list["Problem"] = Relationship(back_populates="creator")

    creator: "User" = Relationship(
        back_populates="users", sa_relationship_kwargs={"remote_side": "[User.id]"}
    )

    @field_validator("permissions")
    def validate_permissions(cls, v):
        if v not in ["standard", "admin"]:
            raise ValueError("Permissions must be either 'standard' or 'admin'")
        return v
