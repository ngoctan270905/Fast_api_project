# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings

# Create context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hàm băm mật khẩu
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Hàm xác minh mật khẩu với password và hash_password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# hàm tạo access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "scope": "access_token"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_scoped_token(subject: str, scope: str, expires_in_minutes: int) -> str:
    """
    Creates a generic JWT with a specific subject and scope.
    Used for things like email verification, password reset, etc.
    """
    expire = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    to_encode = {
        "exp": expire,
        "sub": subject,
        "scope": scope,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_scoped_token(token: str, required_scope: str) -> str:
    """
    Verifies a scoped JWT. It checks the signature, expiry, and scope.
    
    Args:
        token: The JWT string to verify.
        required_scope: The scope the token must have (e.g., "access_token", "email_verification").
        
    Returns:
        The subject (sub) of the token if validation is successful.
        
    Raises:
        HTTPException: If the token is invalid, expired, or has the wrong scope.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        token_scope = payload.get("scope")
        subject = payload.get("sub")
        
        if subject is None:
            raise credentials_exception
            
        if token_scope != required_scope:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token scope. Required: {required_scope}",
            )
            
        return subject

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTError:
        raise credentials_exception

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT refresh token với scope 'refresh_token'.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "scope": "refresh_token"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt