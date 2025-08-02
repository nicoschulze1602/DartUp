# app/routes/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import UserCreate, UserOut, User
from app.auth.auth_utils import hash_password, verify_password, create_access_token, get_current_user
from app.database import get_db
from datetime import datetime, UTC

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user by saving their data to the database.
    """
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password and create new user
    hashed_pw = hash_password(user.password)
    new_user = User(
        username=user.username,
        password_hash=hashed_pw,
        created_at=datetime.now(UTC)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login")
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Log in a user by verifying their credentials and issuing a token.
    """
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalars().first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.
    """
    return {"user": current_user}