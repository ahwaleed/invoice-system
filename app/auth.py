from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, RoleEnum
from .database import get_db

# -- Config --
SECRET_KEY = "replace-with-real-secret"
ALGORITHM = "HS256"
TOKEN_LIFETIME_MIN = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# -- Helpers --
def hash_pwd(pwd: str) -> str:
    return pwd_context.hash(pwd)


def verify_pwd(pwd: str, hashed: str) -> bool:
    return pwd_context.verify(pwd, hashed)


async def authenticate(db: AsyncSession, username: str, password: str):
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not verify_pwd(password, user.password_hash):
        return None
    return user


def create_token(payload: dict) -> str:
    to_encode = payload.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_LIFETIME_MIN)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: int = int(data.get("sub", 0))
    except (JWTError, ValueError):
        raise cred_exc
    user = await db.get(User, uid)
    if not user:
        raise cred_exc
    return user


def role_guard(role: RoleEnum):
    async def _guard(user: Annotated[User, Depends(current_user)]):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _guard

current_employee = role_guard(RoleEnum.Employee)
current_manager = role_guard(RoleEnum.Manager)
