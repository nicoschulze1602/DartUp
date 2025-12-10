from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# 1) Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 👉 Tests setzen TESTING=1 → dann bauen wir KEIN Postgres-Engine
TESTING = os.getenv("TESTING") == "1"

if not DATABASE_URL and not TESTING:
    raise ValueError("DATABASE_URL is not set in the environment.")

# 2) Engine nur erstellen, wenn wir NICHT im Test laufen
engine = None
if not TESTING:
    engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = None
if not TESTING:
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

Base = declarative_base()

async def get_db():
    """
    Normaler DB-Zugriff (nur außerhalb der Tests).
    In Tests wird get_db per dependency_overrides ersetzt.
    """
    if TESTING:
        raise RuntimeError("get_db should be overridden during testing.")

    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """
    Nur für Entwicklung.
    """
    if TESTING:
        return  # Tests brauchen keine Init-DB

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)