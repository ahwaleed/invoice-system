from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, PositiveFloat, constr


# ---------- AUTH ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


# ---------- USER ----------
class UserCreate(BaseModel):
    username: str
    password: str
    role: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


# ---------- INVOICE ----------
class InvoiceBase(BaseModel):
    invoice_number: constr(max_length=64)
    date: date
    amount: PositiveFloat
    description: Optional[str] = None


class InvoiceOut(InvoiceBase):
    id: int
    status: str
    manager_comment: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- HISTORY ----------
class HistoryEvent(BaseModel):
    ts: datetime
    actor: Optional[str] = None
    action: str

    class Config:
        from_attributes = True