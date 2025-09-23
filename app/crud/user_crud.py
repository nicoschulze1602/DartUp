from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from datetime import datetime, UTC
from passlib.context import CryptContext

# Passwort-Hasher konfigurieren
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def create_user(db: AsyncSession, username: str, email: str, password: str) -> User:
    """
    Neuen User in der DB speichern (Passwort wird automatisch gehasht).
    """
    new_user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),  # <-- Hashing hier
        created_at=datetime.now(UTC)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()