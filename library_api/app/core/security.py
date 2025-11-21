# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings

# Create context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a standard JWT access token with an 'access_token' scope.
    """
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