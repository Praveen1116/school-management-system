from pydantic import BaseModel

class DashboardStats(BaseModel):
    total_students: int
    total_teachers: int
    total_classes: int
    todays_attendance_rate: float
    total_fees_outstanding: int
    recent_audit_logs: list[dict]

