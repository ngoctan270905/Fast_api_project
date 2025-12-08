from typing import Annotated
from fastapi import APIRouter, Depends, status, Query

from app.api.deps import get_user_service
from app.core.dependencies import get_current_admin_user, get_current_active_user
from app.models.users import User
from app.schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserListResponse, 
    UserChangePasswordRequest
)
from app.services.user_service import UserService

router = APIRouter()


@router.post("/me/change-password", response_model=UserResponse)
async def change_current_user_password(
    password_data: UserChangePasswordRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Change the current logged-in user's password.
    """
    updated_user = await user_service.change_user_password(
        current_user=current_user,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    return updated_user











