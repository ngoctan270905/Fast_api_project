# app/api/deps.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService


# Dependency để lấy UserRepository
def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepository:
    return UserRepository(session)


# Dependency để lấy AuthService
def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> AuthService:
    return AuthService(user_repo)


# Dependency để lấy UserService
def get_user_service(
        user_repo: Annotated[UserRepository, Depends(get_user_repository)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> UserService:
    return UserService(user_repo=user_repo, db_session=session)
