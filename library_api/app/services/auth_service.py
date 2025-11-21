from typing import Optional
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
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
from app.core.oauth import oauth # Import the oauth object
from app.core.config import settings # Import settings

class AuthService:
    """Service for handling authentication business logic (async)."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

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

    async def register(self, user_data: UserRegister) -> UserResponse:
        """
        Registers a new user, sets them as inactive, and sends a verification email.
        """
        if await self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        if await self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            is_active=False  # User is inactive until email is verified
        )
        created_user = await self.user_repo.create(new_user)

        verification_token = create_scoped_token(
            subject=created_user.email,
            scope="email_verification",
            expires_in_minutes=60 * 24  # 24 hours
        )
        await send_verification_email(
            email_to=created_user.email,
            token=verification_token
        )

        return UserResponse.model_validate(created_user)

    async def verify_email(self, token: str) -> UserResponse:
        """
        Verifies a user's email address from a token.
        """
        email = verify_scoped_token(token, required_scope="email_verification")
        
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
            
        user.is_active = True
        user.email_verified = True
        updated_user = await self.user_repo.update(user)
        
        return UserResponse.model_validate(updated_user)

    async def forgot_password(self, email: str):
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

            await send_password_reset_email(
                email_to=user.email,
                token=password_reset_token
            )
        # Always return a success message to the user
        return {"message": "If an account with that email exists, a password reset link has been sent."}

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

    async def login(self, form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
        """
        Logs in a user and returns a token.
        Allows login using either username or email.
        """
        user = await self.user_repo.get_by_username(form_data.username)
        
        # If user not found by username, try to find by email
        if not user:
            user = await self.user_repo.get_by_email(form_data.username) # form_data.username might be an email

        is_password_correct = False
        if user:
            is_password_correct = verify_password(form_data.password, user.hashed_password)

        if not user or not is_password_correct:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password", # Updated detail message
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user. Please verify your email first."
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )

        return Token(access_token=access_token)

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