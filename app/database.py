# app/database.py
import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

# --------------------------------------------------------------------------- #
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./invoice.db",
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Shared metadata base for ORM models."""
    pass


# ---------- FastAPI dependency --------------------------------------------- #
async def get_db() -> AsyncSession:
    """
    Yields an AsyncSession and guarantees closure after request.
    Use as `Depends(get_db)` inside routes/services.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
