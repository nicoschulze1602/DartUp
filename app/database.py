# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# 1) Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment.")

# 2) Create async engine (connection to Postgres)
engine = create_async_engine(DATABASE_URL, echo=True)

# 3) Session factory for async DB sessions
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# 4) Base class for all models
Base = declarative_base()

# 5) Dependency for FastAPI routes
async def get_db():
    """
    Creates a new database session for a request
    and closes it automatically afterwards.
    """
    async with AsyncSessionLocal() as session:
        yield session


# 6) Function to create all tables
async def init_db():
    """
    Droppt ALLE Tabellen und erstellt sie neu.
    Nur für Dev/Reset nutzen – nicht in Produktion!
    """
    async with engine.begin() as conn:
        # ALLE Tabellen löschen
        await conn.run_sync(Base.metadata.drop_all)
        # Tabellen neu anlegen
        await conn.run_sync(Base.metadata.create_all)