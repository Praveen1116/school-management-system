import uuid
from datetime import date, datetime
from pydantic import BaseModel

class StudentCreate(BaseModel):
    guardian_id: uuid.UUID
    full_name: str
    roll_number: str
    date_of_birth: date

class StudentUpdate(BaseModel):
    guardian_id: uuid.UUID | None = None
    full_name: str | None = None
    roll_number: str | None = None
    date_of_birth: date | None = None

class StudentResponse(BaseModel):
    id: uuid.UUID
    guardian_id: uuid.UUID
    full_name: str
    roll_number: str
    date_of_birth: date
    is_active: bool
    created_at: datetime

