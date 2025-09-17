'''
# jwt_handler.py

import os
from datetime import datetime, timedelta, UTC

from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Load environment variables (e.g. SECRET_KEY from .env)
load_dotenv()

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dependency to extract the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Creates a JWT access token with optional expiration.

    Args:
        data: A dictionary of claims (e.g. {"sub": username}).
        expires_delta: Optional expiration timedelta.

    Returns:
        A JWT as a string.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> str:
    """
    Decodes and verifies a JWT access token and extracts the username.

    Args:
        token: The JWT access token.

    Returns:
        The username stored in the token's 'sub' claim.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise ValueError("Username not found in token")
        return username
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI dependency to retrieve the current authenticated user
    from the JWT token provided in the Authorization header.

    Args:
        token: The Bearer token, automatically extracted via Depends.

    Returns:
        A dictionary containing the username.

    Raises:
        HTTPException: If the token is invalid or missing.
    """
    username = verify_token(token)
    return {"username": username}
'''