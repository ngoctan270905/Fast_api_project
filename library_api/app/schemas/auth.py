from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ===== Request Schemas =====

class UserRegister(BaseModel):
    """Schema for new user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

class EmailVerificationRequest(BaseModel):
    """Schema for the email verification request."""
    token: str

class ForgotPasswordRequest(BaseModel):
    """Schema for the forgot password request."""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Schema for the reset password request."""
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)

# ===== Response Schemas =====

class Token(BaseModel):
    """Schema for the token response."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for the data inside the token."""
    user_id: Optional[int] = None
    username: Optional[str] = None

class UserResponse(BaseModel):
    """Schema for user responses (password is not returned)."""
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    email_verified: bool
    is_social_login: bool  # Add this field
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows conversion from ORM model