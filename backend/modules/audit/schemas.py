import uuid
from typing import Any
from datetime import datetime
from pydantic import BaseModel

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    actor_id: uuid.UUID
    actor_email: str | None = None
    action: str
    entity_type: str
    entity_id: uuid.UUID
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    created_at: datetime

