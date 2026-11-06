import uuid
from datetime import date, datetime
from pydantic import BaseModel

class InvoiceCreate(BaseModel):
    student_id: uuid.UUID
    description: str
    amount_due: int  # in paise
    due_date: date

class InvoiceUpdate(BaseModel):
    description: str | None = None
    amount_due: int | None = None
    due_date: date | None = None

class InvoiceResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    description: str
    amount_due: int
    due_date: date
    created_at: datetime

class PaymentCreate(BaseModel):
    amount_paid: int  # in paise
    payment_ref: str

class PaymentResponse(BaseModel):
    id: uuid.UUID
    invoice_id: uuid.UUID
    amount_paid: int
    payment_ref: str
    paid_at: datetime

class BalanceResponse(BaseModel):
    amount_due: int
    total_paid: int
    outstanding: int
    status: str  # "paid", "partial", "unpaid"

