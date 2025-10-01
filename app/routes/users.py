from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import timedelta

from app.models.user import User
from app.schemas.user_schemas import UserCreate, UserOut, UserLogin
from app.auth.auth_utils import hash_password, verify_password, get_current_user
from app.auth.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db
from app.crud.user_crud import get_user_by_username, create_user, get_all_users

router = APIRouter(prefix="/users", tags=["Users"])


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
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authentifiziert einen User und gibt ein JWT zurück.
    """
    # User in DB suchen
    user: User = await get_user_by_username(db, login_data.username)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Debug-Ausgaben
    print("👉 Eingabe-PW:", login_data.password)
    print("👉 Hash aus DB:", user.password_hash)

    # Passwort prüfen
    if not verify_password(login_data.password, user.password_hash):
        print("❌ Passwortprüfung fehlgeschlagen")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    print("✅ Passwortprüfung erfolgreich")

    # Token erstellen
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Gibt das Profil des eingeloggten Users zurück.
    """
    return UserOut.model_validate(current_user)


@router.get("/", response_model=List[UserOut])
async def get_all_users_endpoint(db: AsyncSession = Depends(get_db)):
    """
    Gibt alle User zurück (ohne Passwörter).
    """
    return await get_all_users(db)

