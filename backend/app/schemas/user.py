from typing import Optional

from pydantic import field_validator
from sqlmodel import SQLModel

from .base import PublicBase


class UserBase(SQLModel):
    name: str
    permissions: str = "standard"

    @field_validator("permissions")
    def validate_permissions(cls, v):
        if v not in ["standard", "admin"]:
            raise ValueError("Permissions must be either 'standard' or 'admin'")
        return v


class UserCreate(UserBase):
    pass


class UserPublic(UserBase, PublicBase):
    pass


class UserUpdate(SQLModel):
    name: Optional[str] = None
    permissions: Optional[str] = None

    @field_validator("permissions")
    def validate_permissions(cls, v):
        if v is not None and v not in ["standard", "admin"]:
            raise ValueError("Permissions must be either 'standard' or 'admin'")
        return v
