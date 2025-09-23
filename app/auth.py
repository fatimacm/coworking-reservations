from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.schemas import UserResponse
import os
from dotenv import load_dotenv

load_dotenv()

# Validate that SECRET_KEY exists
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in environment variables. Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(user: UserResponse, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT token for a specific user.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": user.email,           
        "user_id": user.id,          
        "role": user.role,        
        "exp": expire      
    }
    
    if getattr(user, "username", None):
        to_encode["username"] = user.username
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verify token and return full payload with user information.
    Throws an HTTPException if the token is invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        required = ["sub", "user_id", "role"]
        for field in required:
            if not payload.get(field):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token: missing field {field}"
                )
        
        return {
            "email": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "role": payload.get("role"),
            "username": payload.get("username"),
            "exp": payload.get("exp")
        }
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Token: {str(e)}"
        )


def unsafe_decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode tokens WITHOUT validating errors.
    Use only for debugging, never on production endpoints.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
