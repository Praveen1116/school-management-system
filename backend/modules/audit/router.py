import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, require_admin, paginated_response
from modules.audit.service import list_audit_logs

router = APIRouter()

@router.get("")
async def get_audit_logs(
    entity_type: str | None = Query(None),
    entity_id: uuid.UUID | None = Query(None),
    actor_id: uuid.UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only endpoint to inspect audit trail logs with filtering and pagination."""
    items, total = await list_audit_logs(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit
    )
    return paginated_response(data=items, page=page, limit=limit, total=total)

