from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, success_response
from modules.setup.schemas import SetupRequest, SetupStatusResponse, SetupResponse
from modules.setup import service as setup_service

router = APIRouter()

@router.get("/status")
async def get_status(db: AsyncSession = Depends(get_db)):
    """Returns whether the one-time school setup is required."""
    is_required, school = await setup_service.get_setup_status(db)
    data = SetupStatusResponse(
        is_setup_required=is_required,
        school_name=school.school_name if school else None,
        school_code=school.school_code if school else None,
    ).model_dump()
    return success_response(data=data, message="Setup status retrieved")

@router.post("", status_code=status.HTTP_201_CREATED)
async def setup_instance(payload: SetupRequest, db: AsyncSession = Depends(get_db)):
    """Bootstraps the school profile and initial administrator account. Permanent 403 once completed."""
    school, admin = await setup_service.perform_initial_setup(db, payload)
    data = SetupResponse(
        school_name=school.school_name,
        school_code=school.school_code,
        admin_email=admin.email,
        admin_name=admin.full_name or admin.email,
    ).model_dump()
    return success_response(data=data, message="School and administrator initialized successfully")

