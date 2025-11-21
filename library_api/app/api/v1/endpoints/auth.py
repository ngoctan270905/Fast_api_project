# app/api/v1/endpoints/auth.py
from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service
from app.core.dependencies import get_current_active_user
from app.models.users import User
from app.schemas.auth import (
    UserRegister, 
    Token, 
    UserResponse, 
    EmailVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from app.services.auth_service import AuthService

router = APIRouter()

# ==================== REGISTER ====================
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserRegister,
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Register a new user.
    - Creates an inactive user.
    - Sends a verification email.
    - Does NOT return a login token.
    """
    return await auth_service.register(user_data)

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
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Log in with OAuth2PasswordRequestForm.
    """
    return await auth_service.login(form_data)

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
@router.post("/logout")
async def logout(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Logout.
    Note: With stateless JWT, the server doesn't store the token.
    The client needs to delete the token on its side.
    """
    return {
        "message": f"User {current_user.username} has been logged out successfully.",
        "detail": "Please delete the access token on the client side."
    }
