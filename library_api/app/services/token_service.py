import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from app.repositories.token_repository import TokenRepository
from app.models.users import User

class TokenService:

    def __init__(self, token_repo: TokenRepository):
        self.token_repo = token_repo

    # hàm xử lí logic thêm refresh_token
    async def create_refresh_token(self, user: User, expires_delta: timedelta = timedelta(days=30)) -> str:
        # tạo 1 chuỗi ngẫu nhiên
        raw_token = secrets.token_urlsafe(64)
        # tính thời gian refresh_token hết hạn
        expires_at = datetime.utcnow() + expires_delta
        await self.token_repo.create_refresh_token(
            token=raw_token,
            user_id=user.id,
            expires_at=expires_at
        )
        
        return raw_token

    # hàm xử lí logic xác thực refresh token từ client
    async def verify_refresh_token(self, token: str) -> int:
        # tìm kiếm token
        token_obj = await self.token_repo.get_refresh_token(token)
        # ko có token => 401
        if not token_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        # nếu token đã bị thu hồi => 401
        if token_obj.revoked_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )
        # nếu token hết hạn => 401
        if token_obj.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )

        return token_obj.user_id

    # hàm xử lí login thu hồi refresh token
    async def revoke_refresh_token(self, token: str):
        revoked_token = await self.token_repo.revoke_refresh_token(token)
        # nếu refresh token ko tồn tại => 404
        if not revoked_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refresh token not found"
            )
        return {"message": "Refresh token has been successfully revoked."}

