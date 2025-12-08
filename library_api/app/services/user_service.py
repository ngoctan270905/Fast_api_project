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

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

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
