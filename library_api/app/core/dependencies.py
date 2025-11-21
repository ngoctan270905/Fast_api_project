# app/core/dependencies.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.security import verify_scoped_token
from app.models.users import User

# Re-add the DbSession type alias that was accidentally removed
DbSession = Annotated[AsyncSession, Depends(get_session)]

# OAuth2 scheme - specifies the endpoint to get the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> User:
    """
    Dependency to get the current user from a JWT access token.
    This function is responsible for validating the token and fetching the user from the DB.
    """
    user_id = verify_scoped_token(token, required_scope="access_token")
    
    # Query user from the database
    statement = select(User).where(User.id == int(user_id))
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to get the current user and ensure they are active.
    This is the dependency that should be used for most protected endpoints.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user. Please verify your email.")
    return current_user

async def get_current_admin_user(
        current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Dependency to ensure the current user is an admin.
    Note: It depends on get_current_active_user, so it also ensures the user is active.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Admin privileges required."
        )
    return current_user

