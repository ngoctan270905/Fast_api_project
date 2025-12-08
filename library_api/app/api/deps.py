# app/api/deps.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.category_repository import CategoryRepository
from app.services.auth_service import AuthService
from app.services.author_service import AuthorService
from app.services.book_service import BookService
from app.services.user_service import UserService
from app.services.token_service import TokenService
from app.services.category_service import CategoryService

# Dependency để lấy CategoryRepository
def get_category_repository() -> CategoryRepository:
    return CategoryRepository()

# # Dependency để lấy AuthorRepository
def get_author_repository() -> AuthorRepository:
    return AuthorRepository()

# Dependency để lấy BookRepository
def get_book_repository() -> BookRepository:
    return BookRepository()

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

# Dependency để lấy CategoryService
def get_category_service() -> CategoryService:
    category_repo = get_category_repository()
    return CategoryService(category_repo=category_repo)

def get_author_service() -> AuthorService:
    author_repo = get_author_repository()
    return AuthorService(author_repo=author_repo)

def get_book_service() -> BookService:
    book_repo = get_book_repository()
    category_repo = get_category_repository()
    author_repo = get_author_repository()
    return BookService(book_repo=book_repo, category_repo=category_repo, author_repo=author_repo)