from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import AppException
from modules.setup.model import School
from modules.setup.schemas import SetupRequest
from modules.users.model import User
from modules.auth.utils import hash_password
from modules.audit import service as audit_service

async def get_setup_status(db: AsyncSession) -> tuple[bool, School | None]:
    """Returns whether initial setup is required (zero users in database)."""
    user_count_result = await db.execute(select(func.count()).select_from(User))
    user_count = user_count_result.scalar_one()

    if user_count == 0:
        return True, None

    school_result = await db.execute(select(School).order_by(School.created_at.desc()).limit(1))
    school = school_result.scalar_one_or_none()
    return False, school

async def perform_initial_setup(db: AsyncSession, payload: SetupRequest) -> tuple[School, User]:
    """Executes the one-time school and first-admin creation if zero users exist."""
    is_required, _ = await get_setup_status(db)
    if not is_required:
        raise AppException(
            status_code=403,
            code="SETUP_ALREADY_COMPLETED",
            message="Setup has already been completed. This instance is locked."
        )

    # 1. Create School record
    school = School(
        school_name=payload.school_name.strip(),
        school_code=payload.school_code.strip().upper()
    )
    db.add(school)
    await db.flush()

    # 2. Create Initial Administrator user
    admin_user = User(
        email=payload.email.lower().strip(),
        password_hash=hash_password(payload.password),
        role="admin",
        is_active=True,
        full_name=payload.full_name.strip()
    )
    db.add(admin_user)
    await db.flush()

    # 3. Log Audit Record
    await audit_service.log_action(
        db=db,
        actor_id=admin_user.id,
        actor_email=admin_user.email,
        action="INITIAL_SETUP",
        entity_type="school",
        entity_id=str(school.id),
        old_value=None,
        new_value={
            "school_name": school.school_name,
            "school_code": school.school_code,
            "admin_email": admin_user.email,
            "admin_name": admin_user.full_name
        }
    )

    await db.commit()
    await db.refresh(school)
    await db.refresh(admin_user)

    return school, admin_user

