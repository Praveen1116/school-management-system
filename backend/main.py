from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import settings
from dependencies import AppException

# Import routers from all 12 modules
from modules.auth.router import router as auth_router
from modules.users.router import router as users_router
from modules.students.router import router as students_router
from modules.teachers.router import router as teachers_router
from modules.classes.router import (
    router as classes_router,
    enrollments_router,
    assignments_router
)
from modules.subjects.router import router as subjects_router
from modules.attendance.router import router as attendance_router
from modules.exams.router import (
    router as exams_router,
    grading_rules_router,
    results_router
)
from modules.fees.router import (
    router as fees_router,
    student_fees_router
)
from modules.guardian.router import router as guardian_router
from modules.reports.router import (
    router as reports_router,
    dashboard_router
)
from modules.audit.router import router as audit_router

app = FastAPI(
    title="School Management System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handlers enforcing Standard Response Shape:
# {"success": false, "error": {"code": "...", "message": "..."}}

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    code = "HTTP_ERROR"
    message = str(detail)
    if isinstance(detail, dict):
        code = detail.get("code", code)
        message = detail.get("message", message)
    elif exc.status_code == 401:
        code = "UNAUTHORIZED"
        message = "Could not validate credentials"
    elif exc.status_code == 403:
        code = "FORBIDDEN"
        message = "Access forbidden"
    elif exc.status_code == 404:
        code = "NOT_FOUND"
        message = "Resource not found"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else {}
    msg = first_error.get("msg", "Invalid request body or parameters")
    loc = " -> ".join(str(l) for l in first_error.get("loc", []))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": f"{loc}: {msg}" if loc else msg
            }
        }
    )

# Root health check endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }

# Register all 12 modules exactly as specified
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(students_router, prefix="/api/students", tags=["students"])
app.include_router(teachers_router, prefix="/api/teachers", tags=["teachers"])
app.include_router(classes_router, prefix="/api/classes", tags=["classes"])
app.include_router(subjects_router, prefix="/api/subjects", tags=["subjects"])
app.include_router(attendance_router, prefix="/api/attendance", tags=["attendance"])
app.include_router(exams_router, prefix="/api/exams", tags=["exams"])
app.include_router(fees_router, prefix="/api/fees", tags=["fees"])
app.include_router(guardian_router, prefix="/api/guardian", tags=["guardian"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
app.include_router(audit_router, prefix="/api/audit-logs", tags=["audit"])

# Direct path aliases specified in route requirements
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["reports"])
app.include_router(grading_rules_router, prefix="/api/grading-rules", tags=["exams"])
app.include_router(results_router, prefix="/api/results", tags=["exams"])
app.include_router(enrollments_router, prefix="/api/enrollments", tags=["classes"])
app.include_router(assignments_router, prefix="/api/assignments", tags=["classes"])
app.include_router(student_fees_router, prefix="/api/students", tags=["fees"])

