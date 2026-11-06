import uuid
from datetime import date, datetime
from pydantic import BaseModel

class GradingRuleCreate(BaseModel):
    name: str  # Rule set name, e.g. "Standard 2026"
    grade_label: str  # e.g. "A", "B", "C", "D", "F"
    min_marks: int
    max_marks: int

class GradingRuleUpdate(BaseModel):
    name: str | None = None
    grade_label: str | None = None
    min_marks: int | None = None
    max_marks: int | None = None

class GradingRuleResponse(BaseModel):
    id: uuid.UUID
    name: str
    grade_label: str
    min_marks: int
    max_marks: int

class ExamCreate(BaseModel):
    subject_id: uuid.UUID
    grading_rule_set_name: str
    name: str
    total_marks: int
    exam_date: date

class ExamUpdate(BaseModel):
    name: str | None = None
    total_marks: int | None = None
    exam_date: date | None = None
    grading_rule_set_name: str | None = None

class ExamResponse(BaseModel):
    id: uuid.UUID
    subject_id: uuid.UUID
    grading_rule_set_name: str
    name: str
    total_marks: int
    exam_date: date

class ResultCreate(BaseModel):
    student_id: uuid.UUID
    marks_obtained: int

class ResultUpdate(BaseModel):
    marks_obtained: int

class ResultResponse(BaseModel):
    id: uuid.UUID
    exam_id: uuid.UUID
    student_id: uuid.UUID
    entered_by: uuid.UUID
    marks_obtained: int
    grade: str
    created_at: datetime

