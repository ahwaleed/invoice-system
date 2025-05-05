"""
Monthly spend & KPI reports.
Only managers can call these endpoints.
"""

from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Invoice, User
from ..auth import current_manager   # RBAC: manager‑only access

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly")
async def monthly_report(
    year: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(current_manager),
):
    """
    Returns total reimbursed amount per employee per month:

    [
      {"employee": "alice", "month": "2025-05", "total": 720.49},
      {"employee": "bob",   "month": "2025-05", "total": 145.00}
    ]
    """
    if not (1900 <= year <= 2100):
        raise HTTPException(400, "year parameter out of range")

    # SQLite uses strftime, Postgres uses to_char.  We'll detect driver.
    dialect = db.bind.dialect.name
    if dialect == "sqlite":
        month_expr = func.strftime("%Y-%m", Invoice.date)
        year_filter = func.strftime("%Y", Invoice.date) == str(year)
    else:  # postgresql, mysql etc.
        month_expr = func.to_char(Invoice.date, "YYYY-MM")
        year_filter = func.extract("year", Invoice.date) == year

    stmt = (
        select(
            User.username.label("employee"),
            month_expr.label("month"),
            func.sum(Invoice.amount).label("total"),
        )
        .join(User, User.id == Invoice.uploaded_by)
        .where(year_filter)
        .group_by("employee", "month")
        .order_by("employee", "month")
    )

    rows = (await db.execute(stmt)).mappings().all()
    return rows
