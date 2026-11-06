import uuid
from datetime import datetime
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    role: str  # admin, teacher, guardian

class UserUpdate(BaseModel):
    email: str | None = None
    role: str | None = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime
