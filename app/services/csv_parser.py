import csv
from io import TextIOWrapper
from datetime import datetime
from typing import AsyncGenerator

from fastapi import UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Invoice
from ..schemas import InvoiceBase

HEADER = ["invoice_number", "date", "amount", "description"]
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


async def stream_validate(
    file: UploadFile, db: AsyncSession
) -> AsyncGenerator[InvoiceBase, None]:
    if file.size is not None and file.size > MAX_SIZE:
        raise HTTPException(400, "File larger than 5 MB")

    reader = csv.DictReader(TextIOWrapper(file.file, encoding="utf‑8"))
    if reader.fieldnames != HEADER:
        raise HTTPException(400, "CSV header must be exactly: " + ",".join(HEADER))

    for idx, row in enumerate(reader, start=2):
        try:
            inv = InvoiceBase(
                invoice_number=row["invoice_number"].strip(),
                date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                amount=float(row["amount"]),
                description=row.get("description", ""),
            )
            # uniqueness pre‑check
            if await db.scalar(
                select(Invoice).where(Invoice.invoice_number == inv.invoice_number)
            ):
                raise ValueError("duplicate invoice_number")
            yield inv
        except Exception as e:  # noqa: BLE001
            raise HTTPException(400, f"Row {idx}: {e}")
