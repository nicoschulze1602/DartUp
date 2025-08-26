from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from datetime import datetime, UTC


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def create_user(db: AsyncSession, username: str, hashed_pw: str) -> User:
    new_user = User(
        username=username,
        password_hash=hashed_pw,
        created_at=datetime.now(UTC)  # <--- NEU: explizit setzen
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user