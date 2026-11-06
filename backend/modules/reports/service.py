import uuid
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from modules.students.model import Student
from modules.teachers.model import Teacher
from modules.classes.model import Class
from modules.attendance.model import AttendanceRecord
from modules.fees.model import FeeInvoice, FeePayment
from modules.audit.model import AuditLog
from modules.users.model import User

async def get_dashboard_metrics(db: AsyncSession) -> dict:
    today = date.today()

    # 1. Total active students
    total_students_res = await db.execute(select(func.count(Student.id)).where(Student.is_active.is_(True)))
    total_students = total_students_res.scalar_one()

    # 2. Total active teachers
    total_teachers_res = await db.execute(select(func.count(Teacher.id)).where(Teacher.is_active.is_(True)))
    total_teachers = total_teachers_res.scalar_one()

    # 3. Total classes in current academic year
    # Find max or current year from classes
    max_year_res = await db.execute(select(func.coalesce(func.max(Class.academic_year), 2026)))
    current_year = max_year_res.scalar_one()

    total_classes_res = await db.execute(select(func.count(Class.id)).where(Class.academic_year == current_year))
    total_classes = total_classes_res.scalar_one()

    # 4. Today's attendance rate: (present count today / total students) * 100, rounded to 1dp
    present_today_res = await db.execute(
        select(func.count(AttendanceRecord.id)).where(
            AttendanceRecord.attendance_date == today,
            AttendanceRecord.status == "present"
        )
    )
    present_today = present_today_res.scalar_one()
    todays_attendance_rate = round((present_today / total_students * 100), 1) if total_students > 0 else 0.0

    # 5. Total fees outstanding: SUM(amount_due) - SUM(amount_paid)
    sum_due_res = await db.execute(select(func.coalesce(func.sum(FeeInvoice.amount_due), 0)))
    total_due = sum_due_res.scalar_one()

    sum_paid_res = await db.execute(select(func.coalesce(func.sum(FeePayment.amount_paid), 0)))
    total_paid = sum_paid_res.scalar_one()

    total_fees_outstanding = max(0, total_due - total_paid)

    # 6. Recent 10 audit logs with actor email and action
    recent_logs_query = (
        select(AuditLog, User.email)
        .outerjoin(User, AuditLog.actor_id == User.id)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
    )
    log_rows = (await db.execute(recent_logs_query)).all()
    recent_audit_logs = [
        {
            "id": log.id,
            "actor_id": log.actor_id,
            "actor_email": email,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "created_at": log.created_at
        }
        for log, email in log_rows
    ]

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_classes": total_classes,
        "todays_attendance_rate": todays_attendance_rate,
        "total_fees_outstanding": total_fees_outstanding,
        "recent_audit_logs": recent_audit_logs
    }

async def get_attendance_report(
    db: AsyncSession,
    class_id: uuid.UUID | None = None,
    student_id: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None
) -> list[dict]:
    query = (
        select(
            AttendanceRecord,
            Student.full_name.label("student_name"),
            Student.roll_number.label("roll_number"),
            Class.name.label("class_name"),
            Class.section.label("section")
        )
        .join(Student, AttendanceRecord.student_id == Student.id)
        .join(Class, AttendanceRecord.class_id == Class.id)
    )
    if class_id:
        query = query.where(AttendanceRecord.class_id == class_id)
    if student_id:
        query = query.where(AttendanceRecord.student_id == student_id)
    if date_from:
        query = query.where(AttendanceRecord.attendance_date >= date_from)
    if date_to:
        query = query.where(AttendanceRecord.attendance_date <= date_to)

    query = query.order_by(AttendanceRecord.attendance_date.desc(), Student.roll_number.asc())
    rows = (await db.execute(query)).all()

    return [
        {
            "id": r.AttendanceRecord.id,
            "student_id": r.AttendanceRecord.student_id,
            "student_name": r.student_name,
            "roll_number": r.roll_number,
            "class_id": r.AttendanceRecord.class_id,
            "class_name": f"{r.class_name}-{r.section}",
            "attendance_date": r.AttendanceRecord.attendance_date,
            "session": r.AttendanceRecord.session,
            "status": r.AttendanceRecord.status,
            "created_at": r.AttendanceRecord.created_at
        }
        for r in rows
    ]

async def get_fees_report(db: AsyncSession) -> list[dict]:
    """Returns all invoices where outstanding > 0, ordered by due_date ascending."""
    query = (
        select(FeeInvoice, Student.full_name.label("student_name"))
        .join(Student, FeeInvoice.student_id == Student.id)
        .order_by(FeeInvoice.due_date.asc())
    )
    invoices_with_students = (await db.execute(query)).all()

    report = []
    for inv, student_name in invoices_with_students:
        paid_res = await db.execute(
            select(func.coalesce(func.sum(FeePayment.amount_paid), 0)).where(FeePayment.invoice_id == inv.id)
        )
        total_paid = paid_res.scalar_one()
        outstanding = inv.amount_due - total_paid

        if outstanding > 0:
            status_str = "unpaid" if total_paid == 0 else "partial"
            report.append({
                "invoice_id": inv.id,
                "student_id": inv.student_id,
                "student_name": student_name,
                "description": inv.description,
                "due_date": inv.due_date,
                "amount_due": inv.amount_due,
                "total_paid": total_paid,
                "outstanding": outstanding,
                "status": status_str
            })

    return report

