# app/api/v1/endpoints/auth.py
from typing import Annotated, Optional

import redis.asyncio as redis
from fastapi import APIRouter, Depends, status, Response, Cookie, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service, get_token_service, get_user_repository
from app.core.dependencies import get_current_active_user, get_current_user, oauth2_scheme
from app.core.redis_client import get_redis_client
from app.core.security import create_access_token
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    UserRegister, 
    Token, 
    UserResponse, 
    EmailVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from app.services.auth_service import AuthService
from app.services.token_service import TokenService

router = APIRouter()

# ==================== REGISTER ====================
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserRegister,
        background_tasks: BackgroundTasks,
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Register a new user.
    - Creates an inactive user.
    - Sends a verification email.
    - Does NOT return a login token.
    """
    return await auth_service.register(user_data, background_tasks)

# ==================== VERIFY EMAIL ====================
@router.post("/verify-email", response_model=UserResponse)
async def verify_email(
    request: EmailVerificationRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Verify a user's email address with a token sent to their email.
    """
    return await auth_service.verify_email(request.token)

# ==================== FORGOT/RESET PASSWORD ====================
@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Initiate the password reset process.
    A success message is always returned to prevent email enumeration attacks.
    """
    return await auth_service.forgot_password(request.email)

@router.post("/reset-password", response_model=UserResponse)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Reset a user's password using a valid token.
    """
    return await auth_service.reset_password(request.token, request.new_password)

# ==================== LOGIN ====================
@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)]
):
    """
    Log in with OAuth2PasswordRequestForm.
    Sets an HttpOnly refresh token cookie and returns an access token.
    """
    return await auth_service.login(
        response=response,
        token_service=token_service,
        username=form_data.username,
        password=form_data.password
    )

# ==================== REFRESH TOKEN ====================
@router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_token: str = Cookie(None)
):
    """
    Refresh the access token using the refresh token from the cookie.
    Implements refresh token rotation.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    # Verify the refresh token
    user_id = await token_service.verify_refresh_token(refresh_token)

    # Revoke the old refresh token (implementing rotation)
    await token_service.revoke_refresh_token(refresh_token)

    # Get user object
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not find user"
        )

    # Create new access and refresh tokens
    new_access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    new_refresh_token = await token_service.create_refresh_token(user=user)

    # Set the new refresh token in the cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60  # 30 days
    )

    return Token(access_token=new_access_token)

# ==================== GET USER INFO ====================
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get current user's info (requires authentication).
    """
    return current_user

# ==================== LOGOUT ====================
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    token: Annotated[str, Depends(oauth2_scheme)],
    refresh_token: Optional[str] = Cookie(None),
):
    """
    Đăng xuất người dùng bằng cách:
    1. Vô hiệu hóa access token (thêm vào blacklist).
    2. Thu hồi refresh token (xóa khỏi DB và cookie).
    """
    return await auth_service.logout(
        response=response,
        token_service=token_service,
        redis_client=redis_client,
        access_token=token,
        refresh_token=refresh_token
    )
