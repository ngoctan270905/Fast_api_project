from typing import Annotated
from fastapi import Depends
from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository
from app.repositories.exam_paper_repository import ExamPaperRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.section_repository import SectionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.category_repository import CategoryRepository
from app.services.auth_service import AuthService
from app.services.author_service import AuthorService
from app.services.book_service import BookService
from app.services.exam_service import ExamService
from app.services.section_service import SectionService
from app.services.user_service import UserService
from app.services.token_service import TokenService
from app.services.category_service import CategoryService


# Dependency để lấy QuestionRepository
def get_question_repository() -> QuestionRepository:
    return QuestionRepository()


# Dependency để lấy SectionRepository
def get_section_repository() -> SectionRepository:
    return SectionRepository()


# Dependency để lấy ExamPaperRepository
def get_exam_paper_repository() -> ExamPaperRepository:
    return ExamPaperRepository()


# Dependency để lấy ExamRepository
def get_exam_repository() -> ExamRepository:
    return ExamRepository()


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
def get_user_repository() -> UserRepository:
    return UserRepository()


# Dependency để lấy TokenRepository
def get_token_repository() -> TokenRepository:
    return TokenRepository()


# Dependency để lấy TokenService
def get_token_service(
    token_repo: Annotated[TokenRepository, Depends(get_token_repository)]
) -> TokenService:
    return TokenService(token_repo)


# Dependency để lấy AuthService
def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> AuthService:
    return AuthService(user_repo, token_service)


# Dependency để lấy UserService
def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    return UserService(user_repo=user_repo)


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

def get_exam_service() -> ExamService:
    exam_repo = get_exam_repository()
    exam_paper_repo = get_exam_paper_repository()
    section_repo = get_section_repository()
    question_repo = get_question_repository()
    return ExamService(exam_repo=exam_repo, exam_paper_repo=exam_paper_repo, section_repo=section_repo, question_repo=question_repo)

def get_section_service() -> SectionService:
    section_repo = get_section_repository()
    exam_paper_repo = get_exam_paper_repository()
    return SectionService(section_repo=section_repo, exam_paper_repo=exam_paper_repo)