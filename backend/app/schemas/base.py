from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class CreateBase(SQLModel):
    pass


class PublicBase(SQLModel):
    id: int

    created_at: datetime
    last_modified: datetime

    creator_id: int

    valid_from: datetime
    valid_to: Optional[datetime]
    modifier_id: int


class UpdateBase(SQLModel):
    pass
