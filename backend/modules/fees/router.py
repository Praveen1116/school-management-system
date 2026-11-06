import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import (
    get_db,
    get_current_user,
    require_admin,
    success_response,
    AppException
)
from modules.fees.schemas import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    PaymentCreate,
    PaymentResponse,
    BalanceResponse
)
from modules.fees import service as fees_service
from modules.students import service as students_service
from modules.audit import service as audit_service

router = APIRouter()
student_fees_router = APIRouter()

async def verify_invoice_access(user, invoice, db: AsyncSession):
    """Admin or guardian of the student on the invoice."""
    if user.role == "admin":
        return
    if user.role == "guardian":
        student = await students_service.get_student_by_id(db, invoice.student_id)
        if student and student.guardian_id == user.id:
            return
    raise AppException(
        status_code=status.HTTP_403_FORBIDDEN,
        code="FORBIDDEN_ACCESS",
        message="You are not authorized to view this invoice"
    )

@router.get("/invoices")
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin: all invoices; Guardian: only invoices for their own students."""
    if user.role == "admin":
        invoices = await fees_service.list_invoices(db)
    elif user.role == "guardian":
        my_students = await students_service.get_students_by_guardian_id(db, user.id)
        student_ids = [s.id for s in my_students]
        invoices = await fees_service.list_invoices(db, student_ids=student_ids)
    else:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN_ACCESS",
            message="Not authorized to view invoices"
        )

    data = [
        InvoiceResponse(
            id=inv.id,
            student_id=inv.student_id,
            description=inv.description,
            amount_due=inv.amount_due,
            due_date=inv.due_date,
            created_at=inv.created_at
        ).model_dump()
        for inv in invoices
    ]
    return success_response(data=data, message="Invoices retrieved")

@router.post("/invoices", status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Creates a new fee invoice."""
    invoice = await fees_service.create_invoice(
        db,
        student_id=payload.student_id,
        description=payload.description,
        amount_due=payload.amount_due,
        due_date=payload.due_date
    )
    await db.commit()
    await db.refresh(invoice)

    data = InvoiceResponse(
        id=invoice.id,
        student_id=invoice.student_id,
        description=invoice.description,
        amount_due=invoice.amount_due,
        due_date=invoice.due_date,
        created_at=invoice.created_at
    ).model_dump()
    return success_response(data=data, message="Invoice created successfully")

@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin + guardian (own student only)."""
    invoice = await fees_service.get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise AppException(status_code=status.HTTP_404_NOT_FOUND, code="INVOICE_NOT_FOUND", message="Invoice not found")

    await verify_invoice_access(user, invoice, db)

    data = InvoiceResponse(
        id=invoice.id,
        student_id=invoice.student_id,
        description=invoice.description,
        amount_due=invoice.amount_due,
        due_date=invoice.due_date,
        created_at=invoice.created_at
    ).model_dump()
    return success_response(data=data, message="Invoice retrieved")

@router.put("/invoices/{invoice_id}")
async def update_invoice(
    invoice_id: uuid.UUID,
    payload: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Updates invoice description, due date, or amount due."""
    invoice = await fees_service.get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise AppException(status_code=status.HTTP_404_NOT_FOUND, code="INVOICE_NOT_FOUND", message="Invoice not found")

    invoice = await fees_service.update_invoice(
        db, invoice,
        description=payload.description,
        amount_due=payload.amount_due,
        due_date=payload.due_date
    )
    await db.commit()
    await db.refresh(invoice)

    data = InvoiceResponse(
        id=invoice.id,
        student_id=invoice.student_id,
        description=invoice.description,
        amount_due=invoice.amount_due,
        due_date=invoice.due_date,
        created_at=invoice.created_at
    ).model_dump()
    return success_response(data=data, message="Invoice updated successfully")

@router.get("/invoices/{invoice_id}/payments")
async def list_invoice_payments(
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin + guardian (own student): lists payments made for an invoice."""
    invoice = await fees_service.get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise AppException(status_code=status.HTTP_404_NOT_FOUND, code="INVOICE_NOT_FOUND", message="Invoice not found")

    await verify_invoice_access(user, invoice, db)

    payments = await fees_service.list_payments_for_invoice(db, invoice_id)
    data = [
        PaymentResponse(
            id=p.id,
            invoice_id=p.invoice_id,
            amount_paid=p.amount_paid,
            payment_ref=p.payment_ref,
            paid_at=p.paid_at
        ).model_dump()
        for p in payments
    ]
    return success_response(data=data, message="Payments retrieved")

@router.post("/invoices/{invoice_id}/payments", status_code=status.HTTP_201_CREATED)
async def record_payment(
    invoice_id: uuid.UUID,
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Records payment against an invoice and returns updated balance."""
    invoice = await fees_service.get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise AppException(status_code=status.HTTP_404_NOT_FOUND, code="INVOICE_NOT_FOUND", message="Invoice not found")

    # 1. Check payment_ref uniqueness — 409 DUPLICATE_PAYMENT_REF
    existing_pay = await fees_service.get_payment_by_ref(db, payload.payment_ref)
    if existing_pay:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="DUPLICATE_PAYMENT_REF",
            message=f"Payment reference {payload.payment_ref} already exists"
        )

    # 2. Verify amount_paid > 0 — 400 INVALID_PAYMENT_AMOUNT
    if payload.amount_paid <= 0:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_PAYMENT_AMOUNT",
            message="Payment amount must be greater than zero"
        )

    # 3. Create payment
    payment = await fees_service.create_payment(
        db, invoice_id=invoice_id, amount_paid=payload.amount_paid, payment_ref=payload.payment_ref
    )

    # 4. Write to audit_log
    await audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action=audit_service.PAYMENT_RECORDED,
        entity_type="fee_payment",
        entity_id=payment.id,
        new_value={
            "invoice_id": str(invoice_id),
            "amount_paid": payload.amount_paid,
            "payment_ref": payload.payment_ref
        }
    )
    await db.commit()

    # 3. Return updated balance
    balance = await fees_service.compute_invoice_balance(db, invoice_id)
    return success_response(
        data={
            "payment": PaymentResponse(
                id=payment.id,
                invoice_id=payment.invoice_id,
                amount_paid=payment.amount_paid,
                payment_ref=payment.payment_ref,
                paid_at=payment.paid_at
            ).model_dump(),
            "balance": balance
        },
        message="Payment recorded successfully"
    )

@router.get("/invoices/{invoice_id}/balance")
async def get_invoice_balance(
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin + guardian (own student): Computes live balance and status."""
    invoice = await fees_service.get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise AppException(status_code=status.HTTP_404_NOT_FOUND, code="INVOICE_NOT_FOUND", message="Invoice not found")

    await verify_invoice_access(user, invoice, db)

    balance = await fees_service.compute_invoice_balance(db, invoice_id)
    return success_response(data=balance, message="Invoice balance computed")

@router.get("/students/{student_id}/fee-summary")
@student_fees_router.get("/{student_id}/fee-summary")
async def get_student_fee_summary(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin + guardian (own student only): returns all student invoices with computed balances."""
    student = await students_service.get_student_by_id(db, student_id)
    if not student:
        raise AppException(status_code=status.HTTP_404_NOT_FOUND, code="STUDENT_NOT_FOUND", message="Student not found")

    if user.role == "guardian" and student.guardian_id != user.id:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN_ACCESS",
            message="You are not authorized to view fee summary for this student"
        )
    elif user.role != "admin" and user.role != "guardian":
        raise AppException(status_code=status.HTTP_403_FORBIDDEN, code="FORBIDDEN_ACCESS", message="Not authorized")

    summary = await fees_service.get_student_fee_summary(db, student_id)
    return success_response(data=summary, message="Student fee summary retrieved")

