from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select

from .database import engine, Base, SessionLocal
from .models import Ping

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run once at startup, clean up at shutdown."""
    # --- Startup tasks ---
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        if not await session.scalar(select(Ping)):
            session.add(Ping())       # insert first row
            await session.commit()

    yield  # ---- App runs here ----

    # --- Shutdown tasks (optional) ---
    await engine.dispose()


app = FastAPI(
    title="Invoice System – Skeleton",
    lifespan=lifespan,
)


@app.get("/health", tags=["sanity"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
