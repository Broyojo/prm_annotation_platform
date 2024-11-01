from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ModelBase(SQLModel):
    id: int = Field(default=None, primary_key=True)

    created_at: datetime = Field(default_factory=datetime.now, index=True)
    last_modified: datetime = Field(default_factory=datetime.now, index=True)

    creator_id: int = Field(foreign_key="user.id", index=True)

    valid_from: datetime = Field(default_factory=datetime.now, index=True)
    valid_to: Optional[datetime] = Field(default=None, index=True)
    modifier_id: int = Field(foreign_key="user.id", index=True)
