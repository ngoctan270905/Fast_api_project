# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import books, categories, authors, auth, users, social_auth

api_router = APIRouter()

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
