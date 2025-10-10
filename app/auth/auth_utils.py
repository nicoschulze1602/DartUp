from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.user_crud import get_user_by_username
from app.auth.jwt_handler import decode_access_token

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login",scheme_name="JWT")
oauth2_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    token = creds.credentials   # JWT als string
    print("🔑 Erhaltener Token:", token)

    payload = decode_access_token(token)
    print("📦 Decoded payload:", payload)

    username: str = payload.get("sub")
    print("👤 Username aus Token:", username)

    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    print("✅ Gefundener User:", user.username)
    return user