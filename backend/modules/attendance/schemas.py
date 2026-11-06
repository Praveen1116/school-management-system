import uuid
from datetime import date, datetime
from pydantic import BaseModel

class AttendanceCreate(BaseModel):
    student_id: uuid.UUID
    class_id: uuid.UUID
    attendance_date: date
    session: str  # full_day, morning, afternoon
    status: str   # present, absent, late

class AttendanceUpdate(BaseModel):
    status: str   # present, absent, late

class AttendanceResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    class_id: uuid.UUID
    recorded_by: uuid.UUID
    attendance_date: date
    session: str
    status: str
    created_at: datetime

