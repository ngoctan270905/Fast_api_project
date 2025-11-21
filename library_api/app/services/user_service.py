# app/services/user_service.py
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password


class UserService:
    """Service để xử lý business logic cho user (CRUD)"""

    def __init__(self, user_repo: UserRepository, db_session: AsyncSession):
        self.user_repo = user_repo
        self.db_session = db_session

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> (int, List[User]):
        """Lấy danh sách tất cả user với phân trang"""
        
        # Đếm tổng số user
        total_query = select(func.count(User.id))
        total_result = await self.db_session.execute(total_query)
        total = total_result.scalar_one()

        # Lấy user theo phân trang
        query = select(User).offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        users = result.scalars().all()
        
        return total, users

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Lấy user theo ID"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng")
        return user

    async def create_user(self, user_create: UserCreate) -> User:
        """Tạo user mới"""
        # Kiểm tra username đã tồn tại chưa
        if await self.user_repo.get_by_username(user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username đã tồn tại"
            )

        # Kiểm tra email đã tồn tại chưa
        if await self.user_repo.get_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã tồn tại"
            )

        new_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hash_password(user_create.password),
            is_active=user_create.is_active,
            role=user_create.role
        )
        return await self.user_repo.create(new_user)

    async def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        """Cập nhật thông tin user"""
        user_to_update = await self.get_user_by_id(user_id)

        update_data = user_update.model_dump(exclude_unset=True)

        # Kiểm tra username/email mới có bị trùng không
        if "username" in update_data and update_data["username"] != user_to_update.username:
            if await self.user_repo.get_by_username(update_data["username"]):
                raise HTTPException(status_code=400, detail="Username mới đã tồn tại")
        
        if "email" in update_data and update_data["email"] != user_to_update.email:
            if await self.user_repo.get_by_email(update_data["email"]):
                raise HTTPException(status_code=400, detail="Email mới đã tồn tại")

        # Hash password mới nếu có
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        # Cập nhật các trường
        for key, value in update_data.items():
            setattr(user_to_update, key, value)

        return await self.user_repo.update(user_to_update)

    async def delete_user(self, user_id: int) -> None:
        """Xóa user"""
        user_to_delete = await self.get_user_by_id(user_id)
        await self.user_repo.delete(user_to_delete)
        
    async def change_user_password(
        self,
        current_user: User,
        old_password: str,
        new_password: str
    ) -> User:
        """Changes the current user's password."""
        # Verify the old password
        if not verify_password(old_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
        
        # Hash and update the new password
        current_user.hashed_password = hash_password(new_password)
        
        # Save the updated user
        return await self.user_repo.update(current_user)
