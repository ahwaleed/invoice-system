from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import auth as auth_router
from .routers import invoices as invoices_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # -- Startup --
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # -- Shutdown --
    await engine.dispose()

app = FastAPI(title="Invoice Reimbursement System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(invoices_router.router)
