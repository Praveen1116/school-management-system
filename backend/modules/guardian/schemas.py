import uuid
from datetime import date
from pydantic import BaseModel

class GuardianStudentResponse(BaseModel):
    id: uuid.UUID
    guardian_id: uuid.UUID
    full_name: str
    roll_number: str
    date_of_birth: date
    is_active: bool

