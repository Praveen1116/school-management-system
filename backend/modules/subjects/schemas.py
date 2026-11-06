import uuid
from pydantic import BaseModel

class SubjectCreate(BaseModel):
    name: str
    code: str
    total_marks: int

class SubjectUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    total_marks: int | None = None

class SubjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    total_marks: int

