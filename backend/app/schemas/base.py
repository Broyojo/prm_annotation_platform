from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class ReadBase(SQLModel):
    id: int

    creator_id: int
    created_at: datetime
    last_modified: datetime

    version: int
    valid_from: datetime
    valid_to: Optional[datetime]
    modifier_id: int


class UpdateBase(SQLModel):
    pass
