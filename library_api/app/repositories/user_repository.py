from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User
from app.models.oauth_account import OAuthAccount # Import OAuthAccount
import uuid # For generating unique usernames if needed

class UserRepository:
    """Repository để xử lý các thao tác database với User (bất đồng bộ)"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Lấy user theo ID"""
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Lấy user theo username"""
        statement = select(User).where(User.username == username)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Lấy user theo email"""
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create(self, user: User) -> User:
        """Tạo user mới"""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Cập nhật user"""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Xóa user"""
        await self.session.delete(user)
        await self.session.commit()

    async def find_or_create_by_oauth(
        self,
        provider: str,
        account_id: str,
        email: str,
        username: str
    ) -> User:
        """
        Tìm hoặc tạo User và OAuthAccount dựa trên thông tin từ nhà cung cấp OAuth.
        """
        # 1. Check if an OAuthAccount already exists for this provider and account_id
        statement = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.account_id == account_id
        )
        result = await self.session.execute(statement)
        oauth_account = result.scalars().first()

        if oauth_account:
            # If OAuthAccount exists, return the associated User
            await self.session.refresh(oauth_account, attribute_names=["user"])
            if oauth_account.user:
                return oauth_account.user

        # 2. If no OAuthAccount, check if a User exists with this email
        user = await self.get_by_email(email)

        if user:
            # If User exists by email, link the new OAuthAccount to this User
            new_oauth_account = OAuthAccount(
                provider=provider,
                account_id=account_id,
                access_token="dummy_access_token", # Will be updated with real token later
                user_id=user.id
            )
            self.session.add(new_oauth_account)
            await self.session.commit()
            await self.session.refresh(user, attribute_names=["oauth_accounts"])
            return user
        
        # 3. If neither, create a new User and a new OAuthAccount
        # Generate a unique username if the provided one already exists
        base_username = username.replace(" ", "_").lower()
        new_username = base_username
        i = 1
        while await self.get_by_username(new_username):
            new_username = f"{base_username}{i}"
            i += 1

        new_user = User(
            username=new_username,
            email=email,
            # hashed_password is None for social logins
            is_active=True,
            email_verified=True, # Assume verified by provider
            role="user" # Default role
        )
        self.session.add(new_user)
        await self.session.flush() # Flush to get new_user.id
        await self.session.refresh(new_user)

        new_oauth_account = OAuthAccount(
            provider=provider,
            account_id=account_id,
            access_token="dummy_access_token", # Will be updated with real token later
            user_id=new_user.id
        )
        self.session.add(new_oauth_account)
        await self.session.commit()
        await self.session.refresh(new_user, attribute_names=["oauth_accounts"])
        return new_user