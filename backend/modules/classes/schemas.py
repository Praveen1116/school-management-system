import uuid
from pydantic import BaseModel

class ClassCreate(BaseModel):
    name: str
    section: str
    academic_year: int

class ClassUpdate(BaseModel):
    name: str | None = None
    section: str | None = None
    academic_year: int | None = None

class ClassResponse(BaseModel):
    id: uuid.UUID
    name: str
    section: str
    academic_year: int

class EnrollmentCreate(BaseModel):
    student_id: uuid.UUID
    class_id: uuid.UUID
    academic_year: int

class EnrollmentResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    class_id: uuid.UUID
    academic_year: int

class AssignmentCreate(BaseModel):
    class_id: uuid.UUID
    subject_id: uuid.UUID
    teacher_id: uuid.UUID
    academic_year: int

class AssignmentUpdate(BaseModel):
    teacher_id: uuid.UUID | None = None
    academic_year: int | None = None

class AssignmentResponse(BaseModel):
    id: uuid.UUID
    class_id: uuid.UUID
    subject_id: uuid.UUID
    teacher_id: uuid.UUID
    academic_year: int

