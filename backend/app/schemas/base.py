from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class PublicBase(SQLModel):
    # just mirrors some of things in ModelBase

    id: int

    created_at: datetime
    last_modified: datetime

    creator_id: int

    valid_from: datetime
    valid_to: Optional[datetime]
    modifier_id: int
