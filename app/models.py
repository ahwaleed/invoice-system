import enum
from datetime import date, datetime

from sqlalchemy import (
    Enum,
    Integer,
    String,
    Date,
    Float,
    Text,
    ForeignKey,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# ---------- ENUMS ----------
class RoleEnum(str, enum.Enum):
    Employee = "Employee"
    Manager = "Manager"


class StatusEnum(str, enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"


class ActionEnum(str, enum.Enum):
    Approved = "Approved"
    Rejected = "Rejected"


# ---------- MODELS ----------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), nullable=False)

    invoices: Mapped[list["Invoice"]] = relationship(back_populates="uploader")


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_amount_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum), default=StatusEnum.Pending
    )
    uploaded_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    manager_comment: Mapped[str | None] = mapped_column(Text)

    uploader: Mapped["User"] = relationship(back_populates="invoices")
    history: Mapped[list["InvoiceHistory"]] = relationship(back_populates="invoice")


class InvoiceHistory(Base):
    __tablename__ = "invoice_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow, server_default=func.now()
    )
    action: Mapped[ActionEnum] = mapped_column(Enum(ActionEnum))
    actor_id: Mapped[int | None] = mapped_column(Integer)
    invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False
    )

    invoice: Mapped["Invoice"] = relationship(back_populates="history")
