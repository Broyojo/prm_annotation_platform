from database import get_session
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from models import User
from sqlmodel import select

header_scheme = APIKeyHeader(name="x-key")


async def authenticate_user(
    api_key: str = Security(header_scheme), session=Depends(get_session)
) -> User:
    query = select(User).where(User.api_key == api_key)
    user = session.exec(query).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate API key",
        )
    return user
