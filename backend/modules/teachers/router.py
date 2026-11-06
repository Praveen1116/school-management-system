import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, require_admin, success_response, paginated_response, AppException
from modules.teachers.schemas import TeacherCreate, TeacherUpdate, TeacherResponse
from modules.teachers import service as teachers_service
from modules.users import service as users_service
from modules.auth.utils import hash_password
from modules.audit import service as audit_service

router = APIRouter()

@router.get("")
async def list_teachers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only endpoint to list all teachers with pagination."""
    items, total = await teachers_service.list_teachers(db, page=page, limit=limit)
    return paginated_response(data=items, page=page, limit=limit, total=total)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_teacher(
    payload: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Creates both a User (role=teacher) and Teacher record in one atomic transaction."""
    # Check email duplicate
    existing_user = await users_service.get_user_by_email(db, payload.email)
    if existing_user:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="USER_EMAIL_EXISTS",
            message=f"User with email {payload.email} already exists"
        )

    # Check employee code duplicate
    existing_code = await teachers_service.get_teacher_by_code(db, payload.employee_code)
    if existing_code:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="EMPLOYEE_CODE_EXISTS",
            message=f"Teacher with employee code {payload.employee_code} already exists"
        )

    try:
        # Create user account first
        pwd_hash = hash_password(payload.password)
        user = await users_service.create_user(
            db=db,
            email=payload.email,
            password_hash=pwd_hash,
            role="teacher"
        )

        # Create teacher record linked to user
        teacher = await teachers_service.create_teacher_record(
            db=db,
            user_id=user.id,
            full_name=payload.full_name,
            employee_code=payload.employee_code
        )

        # Write audit logs
        await audit_service.log_action(
            db=db,
            actor_id=admin.id,
            action=audit_service.USER_CREATED,
            entity_type="user",
            entity_id=user.id,
            new_value={"email": user.email, "role": "teacher"}
        )
        await audit_service.log_action(
            db=db,
            actor_id=admin.id,
            action="TEACHER_CREATED",
            entity_type="teacher",
            entity_id=teacher.id,
            new_value={"employee_code": teacher.employee_code, "full_name": teacher.full_name}
        )

        await db.commit()
        await db.refresh(teacher)
    except Exception:
        await db.rollback()
        raise

    data = TeacherResponse(
        id=teacher.id,
        user_id=teacher.user_id,
        email=user.email,
        full_name=teacher.full_name,
        employee_code=teacher.employee_code,
        is_active=teacher.is_active
    ).model_dump()
    return success_response(data=data, message="Teacher created successfully")

@router.get("/{teacher_id}")
async def get_teacher(
    teacher_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only endpoint to get single teacher details."""
    teacher = await teachers_service.get_teacher_by_id(db, teacher_id)
    if not teacher:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="TEACHER_NOT_FOUND",
            message="Teacher not found"
        )
    user = await users_service.get_user_by_id(db, teacher.user_id)
    data = TeacherResponse(
        id=teacher.id,
        user_id=teacher.user_id,
        email=user.email if user else None,
        full_name=teacher.full_name,
        employee_code=teacher.employee_code,
        is_active=teacher.is_active
    ).model_dump()
    return success_response(data=data, message="Teacher retrieved")

@router.put("/{teacher_id}")
async def update_teacher(
    teacher_id: uuid.UUID,
    payload: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only endpoint to update teacher details."""
    teacher = await teachers_service.get_teacher_by_id(db, teacher_id)
    if not teacher:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="TEACHER_NOT_FOUND",
            message="Teacher not found"
        )

    if payload.employee_code and payload.employee_code != teacher.employee_code:
        existing_code = await teachers_service.get_teacher_by_code(db, payload.employee_code)
        if existing_code:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                code="EMPLOYEE_CODE_EXISTS",
                message=f"Teacher with employee code {payload.employee_code} already exists"
            )

    old_val = {"full_name": teacher.full_name, "employee_code": teacher.employee_code}
    teacher = await teachers_service.update_teacher_record(
        db=db,
        teacher=teacher,
        full_name=payload.full_name,
        employee_code=payload.employee_code
    )
    new_val = {"full_name": teacher.full_name, "employee_code": teacher.employee_code}

    await audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action="TEACHER_UPDATED",
        entity_type="teacher",
        entity_id=teacher.id,
        old_value=old_val,
        new_value=new_val
    )
    await db.commit()
    await db.refresh(teacher)

    user = await users_service.get_user_by_id(db, teacher.user_id)
    data = TeacherResponse(
        id=teacher.id,
        user_id=teacher.user_id,
        email=user.email if user else None,
        full_name=teacher.full_name,
        employee_code=teacher.employee_code,
        is_active=teacher.is_active
    ).model_dump()
    return success_response(data=data, message="Teacher updated successfully")

@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only endpoint to soft delete a teacher and their user account."""
    teacher = await teachers_service.get_teacher_by_id(db, teacher_id)
    if not teacher:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="TEACHER_NOT_FOUND",
            message="Teacher not found"
        )

    teacher = await teachers_service.soft_delete_teacher_record(db, teacher)
    user = await users_service.get_user_by_id(db, teacher.user_id)
    if user:
        await users_service.soft_delete_user(db, user)

    await audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action="TEACHER_DEACTIVATED",
        entity_type="teacher",
        entity_id=teacher.id,
        old_value={"is_active": True},
        new_value={"is_active": False}
    )
    await db.commit()

    return success_response(
        data={"id": str(teacher.id), "is_active": teacher.is_active},
        message="Teacher deactivated"
    )

