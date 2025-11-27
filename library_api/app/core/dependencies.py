from typing import Annotated

from dns.dnssecalgs import algorithms
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError

from app.core.config import settings
from app.models.users import User
from app.core.database import get_session
from app.core.security import verify_scoped_token
from app.core.redis_client import get_redis_client
from app.services.blacklist_service import BlacklistService
import redis.asyncio as redis

DbSession = Annotated[AsyncSession, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# hàm kiểm tra và lấy thông tin user từ access_token
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: DbSession,
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)]
) -> User:
    try:
        user_id = await verify_scoped_token(
            token,
            required_scope="access_token",
            redis_client=redis_client
        )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user. Please verify your email."
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )
    return current_user
