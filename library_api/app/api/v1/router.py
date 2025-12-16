from fastapi import APIRouter
from app.api.v1.endpoints import books, categories, authors, auth, users, social_auth, exams, section, exam_papers, \
    questions

api_router = APIRouter()

# ====== Exams routes =====
api_router.include_router(
    exams.router,
    prefix="/exams",
    tags=["Exams"]
)

# ====== Exam Papers routes =====
api_router.include_router(
    exam_papers.router,
    prefix="/exam-papers",
    tags=["Exam Papers"]
)

# ===== Sections routes =====
api_router.include_router(
    section.router,
    prefix="/sections",
    tags=["Sections"]
)

# ===== Question routes =====
api_router.include_router(
    questions.router,
    prefix="/questions",
    tags=["Questions"]
)

# ===== Auth routes =====
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"]
)

# Include the new social_auth router
api_router.include_router(
    social_auth.router,
    prefix="", # The endpoints already have their own prefixes like /login/google
    tags=["Social Auth"]
)

# ===== Users routes (Admin only) =====
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# ===== Books routes =====
api_router.include_router(
    books.router,
    prefix="/books",
    tags=["Books"]
)

# ===== Categories routes =====
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"]
)

# ===== Authors routes =====
api_router.include_router(
    authors.router,
    prefix="/authors",
    tags=["Authors"]
)
