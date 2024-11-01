from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class ModelBase(SQLModel):
    def __init_subclass__(cls, creator_relationship, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.creator: User = Relationship(back_populates=creator_relationship)

    id: int = Field(default=None, primary_key=True)

    created_at: datetime = Field(default_factory=datetime.now, index=True)
    last_modified: datetime = Field(default_factory=datetime.now, index=True)

    creator: User
    creator_id: int = Field(foreign_key="user.id", index=True)

    valid_from: datetime = Field(default_factory=datetime.now, index=True)
    valid_to: Optional[datetime] = Field(default=None, index=True)
    modifier_id: int = Field(foreign_key="user.id", index=True)
