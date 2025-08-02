from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from fastapi import Depends
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Async Engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Session Factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Base für deine Modelle
Base = declarative_base()

async def get_db():
    """
    Dependency that provides a database session.
    Automatically closes the session after request.
    """
    async with AsyncSessionLocal() as session:
        yield session