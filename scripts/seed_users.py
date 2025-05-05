#!/usr/bin/env python
"""
scripts/seed_users.py
---------------------

Create demo users for local development:

  $ python scripts/seed_users.py

By default it inserts:
  • alice / secret  (Employee)
  • bob   / secret  (Manager)

If a user already exists it is skipped.

Adjust USER_DATA below or pass --username / --password / --role
to add additional accounts quickly.
"""

import argparse
import asyncio
from typing import Sequence

from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, Base, SessionLocal
from app.models import User, RoleEnum


# --------------------------------------------------------------------------- #
# default users
USER_DATA: Sequence[tuple[str, str, RoleEnum]] = (
    ("alice", "secret", RoleEnum.Employee),
    ("bob", "secret", RoleEnum.Manager),
)


# --------------------------------------------------------------------------- #
async def add_user(
    session: AsyncSession,
    username: str,
    password: str,
    role: RoleEnum,
) -> None:
    exists = await session.scalar(select(User).where(User.username == username))
    if exists:
        print(f"· user {username!r} already present – skipping")
        return

    session.add(
        User(
            username=username,
            password_hash=bcrypt.hash(password),
            role=role,
        )
    )
    await session.commit()
    print(f"· inserted {username!r} ({role.value})")


async def seed(users: Sequence[tuple[str, str, RoleEnum]]) -> None:
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Insert users
    async with SessionLocal() as session:
        for username, password, role in users:
            await add_user(session, username, password, role)


# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Seed demo users into the DB")
    p.add_argument("--username", help="extra username to add")
    p.add_argument("--password", help="password for extra user")
    p.add_argument(
        "--role",
        choices=[r.value for r in RoleEnum],
        help="role for extra user (Employee/Manager)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    custom = []
    if args.username and args.password and args.role:
        custom.append(
            (args.username, args.password, RoleEnum(args.role))
        )

    asyncio.run(seed([*USER_DATA, *custom]))
    print("✅  Seeding complete.")
