from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from datetime import datetime, UTC



async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def create_user(db: AsyncSession, username: str, email: str, password_hash: str) -> User:
    """
    Neuen User in der DB speichern (erhält bereits ein gehashtes Passwort).
    """
    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        created_at=datetime.now(UTC)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()
