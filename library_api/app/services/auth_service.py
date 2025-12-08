from datetime import datetime
from typing import Optional

import redis.asyncio as redis
import time
from jose import jwt, JWTError
from app.services.blacklist_service import BlacklistService
from fastapi import HTTPException, status, Request, Response, BackgroundTasks
from app.models.users import User
from app.schemas.auth import UserRegister, Token, UserResponse
from app.repositories.user_repository import UserRepository
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_scoped_token,
    verify_scoped_token
)
from app.core.email import send_verification_email, send_password_reset_email
from app.core.oauth import oauth
from app.services.token_service import TokenService
from app.core.config import settings

class AuthService:


    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def _map_id(self, user_dict: dict) -> dict:
        if "_id" in user_dict:
            user_dict["id"] = str(user_dict.pop("_id"))
        return user_dict

    async def handle_google_oauth(self, request: Request) -> str:
        """
        Handles the Google OAuth callback, creates/updates the user, and returns a JWT.
        """
        try:
            token = await oauth.google.authorize_access_token(request)
            # Use the userinfo endpoint to get user profile, it's more reliable
            user_info = await oauth.google.userinfo(token=token)

            email = user_info.get('email')
            name = user_info.get('name') or user_info.get('given_name')
            google_account_id = user_info.get('sub')

            if not email or not google_account_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not retrieve essential user information from Google."
                )

            user = await self.user_repo.find_or_create_by_oauth(
                provider="google",
                account_id=google_account_id,
                email=email,
                username=name or email.split('@')[0]
            )
            
            access_token = create_access_token(
                data={"sub": str(user.id), "username": user.username}
            )
            
            return access_token
        except Exception as e:
            # Consider logging the error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication failed: {e}"
            )

    async def handle_github_oauth(self, request: Request) -> str:
        """
        Handles the GitHub OAuth callback, creates/updates the user, and returns a JWT.
        """
        try:
            token = await oauth.github.authorize_access_token(request)
            resp = await oauth.github.get('user', token=token)
            resp.raise_for_status()
            user_info = resp.json()

            # GitHub may not provide a public email, so we need to check
            email = user_info.get('email')
            if not email:
                # If primary email is null, fetch all user emails
                email_resp = await oauth.github.get('user/emails', token=token)
                email_resp.raise_for_status()
                emails = email_resp.json()
                primary_email_obj = next((e for e in emails if e['primary']), None)
                if primary_email_obj:
                    email = primary_email_obj['email']
            
            github_account_id = str(user_info.get('id'))
            name = user_info.get('name') or user_info.get('login')

            if not email or not github_account_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not retrieve essential user information from GitHub."
                )

            user = await self.user_repo.find_or_create_by_oauth(
                provider="github",
                account_id=github_account_id,
                email=email,
                username=name
            )
            
            access_token = create_access_token(
                data={"sub": str(user.id), "username": user.username}
            )
            
            return access_token
        except Exception as e:
            # Consider logging the error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"GitHub authentication failed: {e}"
            )

    async def handle_facebook_oauth(self, request: Request) -> str:
        """
        Handles the Facebook OAuth callback, creates/updates the user, and returns a JWT.
        """
        try:
            token = await oauth.facebook.authorize_access_token(request)
            resp = await oauth.facebook.get(
                'me?fields=id,name,email,picture',
                token=token
            )
            resp.raise_for_status()
            user_info = resp.json()

            facebook_account_id = user_info.get('id')
            email = user_info.get('email')
            name = user_info.get('name')

            if not email or not facebook_account_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not retrieve essential user information from Facebook."
                )

            user = await self.user_repo.find_or_create_by_oauth(
                provider="facebook",
                account_id=facebook_account_id,
                email=email,
                username=name or email.split('@')[0]
            )
            
            access_token = create_access_token(
                data={"sub": str(user.id), "username": user.username}
            )
            
            return access_token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Facebook authentication failed: {e}"
            )


    # Logic đăng kí tài khoản
    async def register(self, user_data: UserRegister, background_tasks: BackgroundTasks) -> UserResponse:
        existing_username = await self.user_repo.get_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{user_data.username}' đã tồn tại"
            )
        existing_email = await self.user_repo.get_by_email(str(user_data.email))
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_data.email}' đã ồn tại"
            )

        new_user_dict = {
            "username": user_data.username,
            "email": str(user_data.email),
            "hashed_password": hash_password(user_data.password),
            "is_active": False,
            "role": "user",
            "email_verified": False,
            "is_social_login": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        created_user = await self.user_repo.create(new_user_dict)

        verification_token = create_scoped_token(
            subject=created_user["email"],
            scope="email_verification",
            expires_in_minutes=60
        )

        background_tasks.add_task(
            send_verification_email,
            email_to=created_user["email"],
            token=verification_token,
        )

        mapped_user = self._map_id(created_user)
        return UserResponse(**mapped_user)


    # Logic xác minh email
    async def verify_email(self, token: str) -> UserResponse:
        email = await verify_scoped_token(token, required_scope="email_verification")
        
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User không tồn tại"
            )
        
        if user.get("email_verified"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được xác minh!"
            )

        update_data = {
            "is_active": True,
            "email_verified": True
        }
        updated_user = await self.user_repo.update(user["_id"], update_data)
        mapped_user = self._map_id(updated_user)
        return UserResponse(**mapped_user)


    async def forgot_password(self, email: str, background_tasks: BackgroundTasks):
        """
        Handles the forgot password request.
        Finds the user, generates a reset token, and sends an email.
        Does not raise an error for non-existent emails to prevent email enumeration attacks.
        """
        user = await self.user_repo.get_by_email(email)
        if user:
            # Create a password reset token that is short-lived
            password_reset_token = create_scoped_token(
                subject=user.email,
                scope="password_reset",
                expires_in_minutes=15  # 15 minutes expiry
            )

            # await send_password_reset_email(
            #     email_to=user.email,
            #     token=password_reset_token
            # )

            background_tasks.add_task(
                send_password_reset_email,
                email_to=user.email,
                token=password_reset_token,
            )
        # Always return a success message to the user
        return {"message": "Đã gửi link khôi phục mật khẩu, vui lòng kiểm tra email"}

    async def reset_password(self, token: str, new_password: str) -> UserResponse:
        """
        Resets a user's password using a valid token.
        """
        email = verify_scoped_token(token, required_scope="password_reset")
        
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.hashed_password = hash_password(new_password)
        updated_user = await self.user_repo.update(user)
        
        return UserResponse.model_validate(updated_user)

    # hàm xử lí logic đăng nhập
    async def login(self, *, response: Response, token_service: TokenService, username: str, password: str) -> Token:
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        # tạo biến trước để kiểm tra mật khẩu là False
        is_password_correct = False
        if user:
            is_password_correct = verify_password(password, user.hashed_password)
        # nếu user ko tồn tại hoặc password sai => 401
        if not user or not is_password_correct:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # kiểm tra trạng thái hoạt động trước khi login
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user. Please verify your email first."
            )
        # Nếu user tồn tại, mật khẩu đúng, đang active
        # Thì gọi hàm create_access_token ở security.py để tạo access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        # Gọi tiếp services để xử lí thêm refresh_token
        refresh_token = await token_service.create_refresh_token(user=user)

        # Đặt refresh token về cooki httpOnly
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",  # Use secure cookies in production
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_SECONDS
        )

        return Token(access_token=access_token)

    # hàm xử lí logic đăng xuất
    async def logout(
            self, *,
            response: Response,
            token_service: TokenService,
            redis_client: redis.Redis,
            access_token: str,
            refresh_token: Optional[str]
    ) -> dict:

        # Thêm token vào ds đen
        try:
            # giải mã token lấy jti exp
            payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_signature": False}
            )
            jti = payload.get("jti") # mã định danh
            exp = payload.get("exp") # thời gian hết hạn
            user_id = payload.get("sub")

            if jti and exp:
                blacklist_service = BlacklistService(redis_client)
                # số giây token còn sống : thời gian hết hạn - tg hiện tại
                ttl = exp - int(time.time())

                if ttl > 0:  # chỉ thêm v àoblacklist nếu token chưa hết hạn
                    await blacklist_service.add_to_blacklist(jti, ttl, user_id=user_id, exp=exp)

        except Exception as e:
            print(f"Lỗi khi thêm vào black list: {e}")

        # revoke refresh token (nếu có)
        if refresh_token:
            try:
                await token_service.revoke_refresh_token(refresh_token)
            except HTTPException as e:
                if e.status_code not in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]:
                    raise e

        # Luôn xóa cookie
        response.delete_cookie(key="refresh_token")

        return {"message": "Bạn đã logout thành công"}

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticates a user (used for OAuth2PasswordBearer).
        """
        user = await self.user_repo.get_by_username(username)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user