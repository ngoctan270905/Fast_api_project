from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
import redis.asyncio as redis
from app.repositories.user_repository import UserRepository
from app.core.security import verify_scoped_token
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any
from app.core.redis_client import get_redis_client
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        redis_client: redis.Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    user_repo = UserRepository()

    try:
        user_id = await verify_scoped_token(
            token,
            required_scope="access_token",
            redis_client=redis_client
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if "_id" in user:
        user["id"] = str(user["_id"])

    return user