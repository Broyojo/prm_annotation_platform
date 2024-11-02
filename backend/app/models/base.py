from datetime import datetime

from sqlmodel import Field, SQLModel


class ModelBase(SQLModel):
    id: int = Field(default=None, primary_key=True, nullable=True)

    created_at: datetime = Field(default_factory=datetime.now, index=True)
    last_modified: datetime = Field(default_factory=datetime.now, index=True)

    creator_id: int = Field(foreign_key="user.id", index=True)
