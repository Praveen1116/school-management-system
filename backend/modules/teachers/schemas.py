import uuid
from pydantic import BaseModel

class TeacherCreate(BaseModel):
    email: str
    password: str
    full_name: str
    employee_code: str

class TeacherUpdate(BaseModel):
    full_name: str | None = None
    employee_code: str | None = None

class TeacherResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email: str | None = None
    full_name: str
    employee_code: str
    is_active: bool
