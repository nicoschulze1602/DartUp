from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user_schemas import UserCreate, UserLogin, UserOut
from app.auth.auth_utils import hash_password, verify_password, create_access_token, get_current_user
from app.database import get_db
from app.crud.user_crud import get_user_by_username, create_user

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user by saving their data to the database.
    """
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(user.password)
    new_user = await create_user(db, user.username, user.email, hashed_pw)
    return new_user


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Log in a user by verifying their credentials and issuing a token.
    """
    db_user = await get_user_by_username(db, user.username)

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password"
        )

    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.
    """
    return current_user