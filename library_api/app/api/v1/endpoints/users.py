# app/api/v1/endpoints/users.py
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


@router.get("/", response_model=UserListResponse)
async def list_users(
        user_service: Annotated[UserService, Depends(get_user_service)],
        current_admin: Annotated[User, Depends(get_current_admin_user)],
        skip: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua"),
        limit: int = Query(10, ge=1, le=100, description="Số lượng bản ghi tối đa")
):
    """
    Lấy danh sách người dùng (chỉ dành cho admin).
    """
    total, users = await user_service.get_all_users(skip=skip, limit=limit)
    return {"total": total, "users": users}


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_create: UserCreate,
        user_service: Annotated[UserService, Depends(get_user_service)],
        current_admin: Annotated[User, Depends(get_current_admin_user)]
):
    """
    Tạo người dùng mới (chỉ dành cho admin).
    """
    new_user = await user_service.create_user(user_create)
    return new_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: int,
        user_service: Annotated[UserService, Depends(get_user_service)],
        current_admin: Annotated[User, Depends(get_current_admin_user)]
):
    """
    Lấy thông tin chi tiết của một người dùng (chỉ dành cho admin).
    """
    user = await user_service.get_user_by_id(user_id)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        user_service: Annotated[UserService, Depends(get_user_service)],
        current_admin: Annotated[User, Depends(get_current_admin_user)]
):
    """
    Cập nhật thông tin người dùng (chỉ dành cho admin).
    """
    updated_user = await user_service.update_user(user_id, user_update)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int,
        user_service: Annotated[UserService, Depends(get_user_service)],
        current_admin: Annotated[User, Depends(get_current_admin_user)]
):
    """
    Xóa người dùng (chỉ dành cho admin).
    """
    await user_service.delete_user(user_id)
    return None
