# app/api/deps.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.category_repository import CategoryRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.token_service import TokenService
from app.services.category_service import CategoryService

def get_category_repository() -> CategoryRepository:
    """Dependency provider cho CategoryRepository."""
    # Trả về một instance mới của CategoryRepository.
    return CategoryRepository()

def get_category_service() -> CategoryService:
    """
    Dependency provider cho CategoryService.
    Hàm này sẽ phụ thuộc vào get_category_repository.
    """
    # Khởi tạo repository trước.
    repo = get_category_repository()
    # Khởi tạo và trả về một instance của CategoryService.
    return CategoryService(category_repo=repo)

# Dependency để lấy UserRepository
def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepository:
    return UserRepository(session)


# Dependency để lấy TokenRepository
def get_token_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> TokenRepository:
    return TokenRepository(session)


# Dependency để lấy AuthService
def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> AuthService:
    return AuthService(user_repo)


# Dependency để lấy TokenService
def get_token_service(
    token_repo: Annotated[TokenRepository, Depends(get_token_repository)]
) -> TokenService:
    return TokenService(token_repo)


# Dependency để lấy UserService
def get_user_service(
        user_repo: Annotated[UserRepository, Depends(get_user_repository)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> UserService:
    return UserService(user_repo=user_repo, db_session=session)