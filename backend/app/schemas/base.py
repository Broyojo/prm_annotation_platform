from datetime import datetime

from sqlmodel import SQLModel


class ReadBase(SQLModel):
    id: int
    creator_id: int
    created_at: datetime
    last_modified: datetime


class UpdateBase(SQLModel):
    pass
