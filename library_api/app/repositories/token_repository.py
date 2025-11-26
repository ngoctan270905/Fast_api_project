from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.models.refresh_token import RefreshToken
import hashlib

class TokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # băm mã refresh token
    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    # thêm refresh token
    async def create_refresh_token(self, token: str, user_id: int, expires_at: datetime) -> str:
        # gọi hash_token để băm mã refresh token ra
        hashed_token = self._hash_token(token)
        # tìm mã refresh token trong db xem đã có chưa
        existing = await self.get_refresh_token(token)
        if existing: # nếu đã có mã refresh token
            raise ValueError("Đã phát hiện xung đột mã refresh token. vui lòng thử lại")

        new_refresh_token = RefreshToken(
            token=hashed_token,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.session.add(new_refresh_token)
        await self.session.commit()
        await self.session.refresh(new_refresh_token)
        return token

    # tìm mã refresh token
    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        hashed_token = self._hash_token(token) # băm token trước
        statement = select(RefreshToken).where(RefreshToken.token == hashed_token) # truy vấn và tìm token
        result = await self.session.execute(statement)
        return result.scalars().first()

    # thu hồi refresh token
    async def revoke_refresh_token(self, token: str) -> Optional[RefreshToken]:
        # tìm kiếm token
        token_obj = await self.get_refresh_token(token)
        if token_obj: # nếu có token
            token_obj.revoked_at = datetime.utcnow() # gán thời điểm token bị vô hiệu
            self.session.add(token_obj)
            await self.session.commit()
            await self.session.refresh(token_obj)
            return token_obj # trả về token đã bị vô hiệu
        return None # ko có thì none

    # xóa refresh token
    async def delete_refresh_token(self, token: str) -> bool:
        hashed_token = self._hash_token(token)
        statement = delete(RefreshToken).where(RefreshToken.token == hashed_token)
        result = await self.session.execute(statement)
        await self.session.commit()
        return result.rowcount > 0 # trả về số dòng đã xóa > 0 True <= 0  False

    # xóa refresh token đã hết hạn
    async def delete_expired_tokens(self) -> int:
        now = datetime.utcnow()
        statement = delete(RefreshToken).where(RefreshToken.expires_at <= now)
        result = await self.session.execute(statement)
        deleted_count = result.rowcount
        await self.session.commit()
        return deleted_count
