import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, require_admin, success_response
from modules.reports import service as reports_service

router = APIRouter()
dashboard_router = APIRouter()

@router.get("/dashboard")
@dashboard_router.get("")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only dashboard metrics."""
    metrics = await reports_service.get_dashboard_metrics(db)
    return success_response(data=metrics, message="Dashboard metrics retrieved")

@router.get("/attendance")
async def get_attendance_report(
    class_id: uuid.UUID | None = Query(None),
    student_id: uuid.UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Filtered attendance report."""
    report = await reports_service.get_attendance_report(
        db, class_id=class_id, student_id=student_id, date_from=date_from, date_to=date_to
    )
    return success_response(data=report, message="Attendance report retrieved")

@router.get("/fees")
async def get_fees_report(
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Fees report with all outstanding invoices ordered by due date."""
    report = await reports_service.get_fees_report(db)
    return success_response(data=report, message="Fees report retrieved")

