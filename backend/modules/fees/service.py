import uuid
from typing import Sequence
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from modules.fees.model import FeeInvoice, FeePayment
from modules.students.model import Student

async def get_invoice_by_id(db: AsyncSession, invoice_id: uuid.UUID) -> FeeInvoice | None:
    result = await db.execute(select(FeeInvoice).where(FeeInvoice.id == invoice_id))
    return result.scalar_one_or_none()

async def list_invoices(
    db: AsyncSession,
    student_ids: list[uuid.UUID] | None = None
) -> Sequence[FeeInvoice]:
    query = select(FeeInvoice).order_by(FeeInvoice.due_date.asc())
    if student_ids is not None:
        query = query.where(FeeInvoice.student_id.in_(student_ids))
    result = await db.execute(query)
    return result.scalars().all()

async def create_invoice(
    db: AsyncSession,
    student_id: uuid.UUID,
    description: str,
    amount_due: int,
    due_date: date
) -> FeeInvoice:
    invoice = FeeInvoice(
        student_id=student_id,
        description=description,
        amount_due=amount_due,
        due_date=due_date
    )
    db.add(invoice)
    await db.flush()
    return invoice

async def update_invoice(
    db: AsyncSession,
    invoice: FeeInvoice,
    description: str | None = None,
    amount_due: int | None = None,
    due_date: date | None = None
) -> FeeInvoice:
    if description is not None:
        invoice.description = description
    if amount_due is not None:
        invoice.amount_due = amount_due
    if due_date is not None:
        invoice.due_date = due_date
    await db.flush()
    return invoice

async def get_payment_by_ref(db: AsyncSession, payment_ref: str) -> FeePayment | None:
    result = await db.execute(select(FeePayment).where(FeePayment.payment_ref == payment_ref))
    return result.scalar_one_or_none()

async def list_payments_for_invoice(db: AsyncSession, invoice_id: uuid.UUID) -> Sequence[FeePayment]:
    query = select(FeePayment).where(FeePayment.invoice_id == invoice_id).order_by(FeePayment.paid_at.asc())
    result = await db.execute(query)
    return result.scalars().all()

async def create_payment(
    db: AsyncSession,
    invoice_id: uuid.UUID,
    amount_paid: int,
    payment_ref: str
) -> FeePayment:
    payment = FeePayment(
        invoice_id=invoice_id,
        amount_paid=amount_paid,
        payment_ref=payment_ref
    )
    db.add(payment)
    await db.flush()
    return payment

async def compute_invoice_balance(db: AsyncSession, invoice_id: uuid.UUID) -> dict:
    """Computes dynamic balance: amount_due, total_paid, outstanding, status."""
    invoice = await get_invoice_by_id(db, invoice_id)
    if not invoice:
        return {}

    sum_query = select(func.coalesce(func.sum(FeePayment.amount_paid), 0)).where(
        FeePayment.invoice_id == invoice_id
    )
    total_paid = (await db.execute(sum_query)).scalar_one()

    # Check payment count for "unpaid" status
    count_query = select(func.count(FeePayment.id)).where(FeePayment.invoice_id == invoice_id)
    payment_count = (await db.execute(count_query)).scalar_one()

    outstanding = invoice.amount_due - total_paid

    if payment_count == 0:
        status_str = "unpaid"
    elif outstanding <= 0:
        status_str = "paid"
    else:
        status_str = "partial"

    return {
        "invoice_id": invoice.id,
        "amount_due": invoice.amount_due,
        "total_paid": total_paid,
        "outstanding": outstanding,
        "status": status_str
    }

async def get_student_fee_summary(db: AsyncSession, student_id: uuid.UUID) -> list[dict]:
    """Returns all invoices for a student with balance computed for each."""
    invoices = await list_invoices(db, student_ids=[student_id])
    summary = []
    for inv in invoices:
        balance = await compute_invoice_balance(db, inv.id)
        summary.append({
            "id": inv.id,
            "description": inv.description,
            "due_date": inv.due_date,
            "amount_due": inv.amount_due,
            "total_paid": balance.get("total_paid", 0),
            "outstanding": balance.get("outstanding", inv.amount_due),
            "status": balance.get("status", "unpaid")
        })
    return summary

