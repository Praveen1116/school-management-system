import uuid
from typing import Any, Sequence
from datetime import date, datetime, time, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from modules.audit.model import AuditLog
from modules.users.model import User

# Consistent Action Constants
STUDENT_CREATED = "STUDENT_CREATED"
STUDENT_UPDATED = "STUDENT_UPDATED"
STUDENT_DEACTIVATED = "STUDENT_DEACTIVATED"
ATTENDANCE_RECORDED = "ATTENDANCE_RECORDED"
ATTENDANCE_UPDATED = "ATTENDANCE_UPDATED"
RESULT_ENTERED = "RESULT_ENTERED"
RESULT_UPDATED = "RESULT_UPDATED"
PAYMENT_RECORDED = "PAYMENT_RECORDED"
USER_CREATED = "USER_CREATED"
USER_DEACTIVATED = "USER_DEACTIVATED"

async def log_action(
    db: AsyncSession,
    actor_id: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    old_value: dict | None = None,
    new_value: dict | None = None
) -> AuditLog:
    """Logs an action synchronously in the same transaction as the parent operation."""
    log_entry = AuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value
    )
    db.add(log_entry)
    await db.flush()
    return log_entry

async def list_audit_logs(
    db: AsyncSession,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    actor_id: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    limit: int = 20
) -> tuple[list[dict], int]:
    """Retrieves paginated audit logs with actor emails."""
    query = select(AuditLog, User.email).outerjoin(User, AuditLog.actor_id == User.id)
    count_query = select(func.count(AuditLog.id))

    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
        count_query = count_query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
        count_query = count_query.where(AuditLog.entity_id == entity_id)
    if actor_id:
        query = query.where(AuditLog.actor_id == actor_id)
        count_query = count_query.where(AuditLog.actor_id == actor_id)
    if date_from:
        start_dt = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
        query = query.where(AuditLog.created_at >= start_dt)
        count_query = count_query.where(AuditLog.created_at >= start_dt)
    if date_to:
        end_dt = datetime.combine(date_to, time.max, tzinfo=timezone.utc)
        query = query.where(AuditLog.created_at <= end_dt)
        count_query = count_query.where(AuditLog.created_at <= end_dt)

    total_res = await db.execute(count_query)
    total = total_res.scalar_one()

    offset = (page - 1) * limit
    query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    rows = (await db.execute(query)).all()

    items = []
    for log, email in rows:
        items.append({
            "id": log.id,
            "actor_id": log.actor_id,
            "actor_email": email,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "created_at": log.created_at
        })

    return items, total

