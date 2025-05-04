from typing import List, Annotated

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload 

from ..database import get_db
from ..models import Invoice, StatusEnum, InvoiceHistory, ActionEnum
from ..schemas import InvoiceOut
from ..auth import current_employee, current_manager, current_user
from ..services.csv_parser import stream_validate

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/upload")
async def upload(
    file: Annotated[UploadFile, File(..., description="CSV file")],
    employee=Depends(current_employee),
    db: AsyncSession = Depends(get_db),
):
    inserted = 0
    async for inv in stream_validate(file, db):
        db.add(Invoice(**inv.model_dump(), uploaded_by=employee.id))
        inserted += 1
    await db.commit()
    return {"inserted": inserted}


@router.get("", response_model=List[InvoiceOut])
async def list_invoices(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Invoice)
    if user.role.value == "Employee":
        stmt = stmt.where(Invoice.uploaded_by == user.id)
    res = await db.execute(stmt)
    return res.scalars().all()


# --- helpers ---------------------------------------------------------------
async def _transition(
    invoice_id: int,
    new_status: StatusEnum,
    comment: str | None,
    manager,
    db: AsyncSession,
):
    inv = await db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(404, "Invoice not found")
    if inv.status != StatusEnum.Pending:
        raise HTTPException(409, "Already processed")

    inv.status = new_status
    inv.manager_comment = comment
    db.add(
        InvoiceHistory(
            action=ActionEnum(new_status.value),
            actor_id=manager.id,
            invoice_id=inv.id,
        )
    )
    await db.commit()
    await db.refresh(inv)
    return inv


@router.post("/{invoice_id}/approve", response_model=InvoiceOut)
async def approve(
    invoice_id: int,
    body: dict | None = None,
    manager=Depends(current_manager),
    db: AsyncSession = Depends(get_db),
):
    return await _transition(
        invoice_id, StatusEnum.Approved, (body or {}).get("comment"), manager, db
    )


@router.post("/{invoice_id}/reject", response_model=InvoiceOut)
async def reject(
    invoice_id: int,
    body: dict | None = None,
    manager=Depends(current_manager),
    db: AsyncSession = Depends(get_db),
):
    return await _transition(
        invoice_id, StatusEnum.Rejected, (body or {}).get("comment"), manager, db
    )


@router.get("/{invoice_id}/history")
async def history(invoice_id: int, db: AsyncSession = Depends(get_db)):
    inv = await db.get(
        Invoice,
        invoice_id,
        options=[selectinload(Invoice.history)],    # ← force eager load
    )
    if not inv:
        raise HTTPException(404, "Invoice not found")

    return [
        {"ts": h.ts, "actor": h.actor_id, "action": h.action.value}
        for h in inv.history
    ]
