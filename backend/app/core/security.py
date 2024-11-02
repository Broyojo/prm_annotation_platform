from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlmodel import select

from app.database import get_session
from app.models.user import User

header_scheme = APIKeyHeader(name="x-key")


async def get_api_user(
    api_key: str = Security(header_scheme), session=Depends(get_session)
) -> User:
    user = session.exec(select(User).where(User.api_key == api_key)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate API key",
        )
    return user
