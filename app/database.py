import os
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

# Read from env var or default to local SQLite file.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite+aiosqlite:///./invoice.db"
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Shared metadata class for models."""
    pass
