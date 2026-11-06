import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import (
    get_db,
    get_current_user,
    require_admin,
    require_teacher,
    success_response,
    AppException
)
from modules.exams.schemas import (
    GradingRuleCreate,
    GradingRuleUpdate,
    GradingRuleResponse,
    ExamCreate,
    ExamUpdate,
    ExamResponse,
    ResultCreate,
    ResultUpdate,
    ResultResponse
)
from modules.exams import service as exams_service
from modules.teachers import service as teachers_service
from modules.teachers.model import Teacher
from modules.classes import service as classes_service
from modules.audit import service as audit_service

router = APIRouter()
grading_rules_router = APIRouter()
results_router = APIRouter()

# --- Grading Rules ---

@router.get("/grading-rules")
@grading_rules_router.get("")
async def list_grading_rules(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_teacher)
):
    """Admin + teacher: Lists all grading rules."""
    rules = await exams_service.list_grading_rules(db)
    data = [
        GradingRuleResponse(
            id=r.id,
            name=r.name,
            grade_label=r.grade_label,
            min_marks=r.min_marks,
            max_marks=r.max_marks
        ).model_dump()
        for r in rules
    ]
    return success_response(data=data, message="Grading rules retrieved")

@router.post("/grading-rules", status_code=status.HTTP_201_CREATED)
@grading_rules_router.post("", status_code=status.HTTP_201_CREATED)
async def create_grading_rule(
    payload: GradingRuleCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Creates a grading rule."""
    rule = await exams_service.create_grading_rule(
        db, payload.name, payload.grade_label, payload.min_marks, payload.max_marks
    )
    await db.commit()
    await db.refresh(rule)

    data = GradingRuleResponse(
        id=rule.id,
        name=rule.name,
        grade_label=rule.grade_label,
        min_marks=rule.min_marks,
        max_marks=rule.max_marks
    ).model_dump()
    return success_response(data=data, message="Grading rule created")

@router.put("/grading-rules/{rule_id}")
@grading_rules_router.put("/{rule_id}")
async def update_grading_rule(
    rule_id: uuid.UUID,
    payload: GradingRuleUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Updates a grading rule."""
    rule = await exams_service.get_grading_rule_by_id(db, rule_id)
    if not rule:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="GRADING_RULE_NOT_FOUND",
            message="Grading rule not found"
        )

    rule = await exams_service.update_grading_rule(
        db, rule, payload.name, payload.grade_label, payload.min_marks, payload.max_marks
    )
    await db.commit()
    await db.refresh(rule)

    data = GradingRuleResponse(
        id=rule.id,
        name=rule.name,
        grade_label=rule.grade_label,
        min_marks=rule.min_marks,
        max_marks=rule.max_marks
    ).model_dump()
    return success_response(data=data, message="Grading rule updated")


# --- Exams ---

@router.get("")
async def list_exams(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_teacher)
):
    """Admin: all exams; Teacher: only assigned subjects."""
    if user.role == "admin":
        exams = await exams_service.list_exams(db)
    else:
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        if not teacher:
            return success_response(data=[], message="No exams found")
        exams = await exams_service.list_exams(db, teacher_id=teacher.id)

    data = [
        ExamResponse(
            id=e.id,
            subject_id=e.subject_id,
            grading_rule_set_name=e.grading_rule_set_name,
            name=e.name,
            total_marks=e.total_marks,
            exam_date=e.exam_date
        ).model_dump()
        for e in exams
    ]
    return success_response(data=data, message="Exams retrieved")

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_exam(
    payload: ExamCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Creates a new exam."""
    exam = await exams_service.create_exam(
        db,
        subject_id=payload.subject_id,
        grading_rule_set_name=payload.grading_rule_set_name,
        name=payload.name,
        total_marks=payload.total_marks,
        exam_date=payload.exam_date
    )
    await db.commit()
    await db.refresh(exam)

    data = ExamResponse(
        id=exam.id,
        subject_id=exam.subject_id,
        grading_rule_set_name=exam.grading_rule_set_name,
        name=exam.name,
        total_marks=exam.total_marks,
        exam_date=exam.exam_date
    ).model_dump()
    return success_response(data=data, message="Exam created successfully")

@router.get("/{exam_id}")
async def get_exam(
    exam_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_teacher)
):
    """Admin + teacher (if assigned to this subject's class)."""
    exam = await exams_service.get_exam_by_id(db, exam_id)
    if not exam:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="EXAM_NOT_FOUND",
            message="Exam not found"
        )

    if user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        # Check if teacher teaches this exam's subject in any class
        if not teacher:
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="TEACHER_NOT_ASSIGNED",
                message="You are not assigned to this subject"
            )
        # Verify assignment
        query = select(ClassSubjectAssignment.id).where(
            ClassSubjectAssignment.teacher_id == teacher.id,
            ClassSubjectAssignment.subject_id == exam.subject_id
        )
        res = (await db.execute(query)).scalar_one_or_none()
        if not res:
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="TEACHER_NOT_ASSIGNED",
                message="You are not assigned to this subject"
            )

    data = ExamResponse(
        id=exam.id,
        subject_id=exam.subject_id,
        grading_rule_set_name=exam.grading_rule_set_name,
        name=exam.name,
        total_marks=exam.total_marks,
        exam_date=exam.exam_date
    ).model_dump()
    return success_response(data=data, message="Exam retrieved")

@router.put("/{exam_id}")
async def update_exam(
    exam_id: uuid.UUID,
    payload: ExamUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Updates exam details."""
    exam = await exams_service.get_exam_by_id(db, exam_id)
    if not exam:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="EXAM_NOT_FOUND",
            message="Exam not found"
        )

    exam = await exams_service.update_exam(
        db, exam,
        name=payload.name,
        total_marks=payload.total_marks,
        exam_date=payload.exam_date,
        grading_rule_set_name=payload.grading_rule_set_name
    )
    await db.commit()
    await db.refresh(exam)

    data = ExamResponse(
        id=exam.id,
        subject_id=exam.subject_id,
        grading_rule_set_name=exam.grading_rule_set_name,
        name=exam.name,
        total_marks=exam.total_marks,
        exam_date=exam.exam_date
    ).model_dump()
    return success_response(data=data, message="Exam updated successfully")


# --- Results ---

@router.get("/{exam_id}/results")
async def get_exam_results(
    exam_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_teacher)
):
    """Admin + teacher (assigned): Lists all results for an exam."""
    exam = await exams_service.get_exam_by_id(db, exam_id)
    if not exam:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="EXAM_NOT_FOUND",
            message="Exam not found"
        )

    if user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        if not teacher:
            raise AppException(status_code=status.HTTP_403_FORBIDDEN, code="FORBIDDEN_ACCESS", message="Not assigned")
        query = select(ClassSubjectAssignment.id).where(
            ClassSubjectAssignment.teacher_id == teacher.id,
            ClassSubjectAssignment.subject_id == exam.subject_id
        )
        if not (await db.execute(query)).scalar_one_or_none():
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="TEACHER_NOT_ASSIGNED",
                message="You are not assigned to this subject"
            )

    results = await exams_service.list_exam_results(db, exam_id)
    return success_response(data=results, message="Exam results retrieved")

@router.post("/{exam_id}/results", status_code=status.HTTP_201_CREATED)
async def enter_exam_result(
    exam_id: uuid.UUID,
    payload: ResultCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_teacher)
):
    """Enters exam result with boundary-inclusive grading rule computation and audit logging."""
    exam = await exams_service.get_exam_by_id(db, exam_id)
    if not exam:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="EXAM_NOT_FOUND",
            message="Exam not found"
        )

    # Teacher assignment check
    if user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        if not teacher or not await classes_service.is_teacher_assigned_to_student_subject(db, teacher.id, payload.student_id, exam.subject_id):
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="TEACHER_NOT_ASSIGNED",
                message="Teacher is not assigned to this subject for this student's class"
            )
        entered_by = teacher.id
    else:
        # Admin entering: use teacher assigned to student's subject, or any teacher fallback
        t_res = await db.execute(select(Teacher).where(Teacher.is_active.is_(True)).limit(1))
        t = t_res.scalar_one_or_none()
        if not t:
            raise AppException(status_code=status.HTTP_400_BAD_REQUEST, code="NO_TEACHERS", message="No teacher found")
        entered_by = t.id

    # 1. Verify marks_obtained <= exam.total_marks
    if payload.marks_obtained > exam.total_marks:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="MARKS_EXCEED_TOTAL",
            message=f"Marks obtained ({payload.marks_obtained}) exceeds total exam marks ({exam.total_marks})"
        )

    # 2. Verify marks_obtained >= 0
    if payload.marks_obtained < 0:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_MARKS",
            message="Marks obtained cannot be negative"
        )

    # 3. Compute grade by querying grading_rules where name = exam.grading_rule_set_name
    grade = await exams_service.compute_grade(db, exam.grading_rule_set_name, payload.marks_obtained)
    if not grade:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="NO_MATCHING_GRADE_RULE",
            message=f"No matching grade rule found for {payload.marks_obtained} marks in rule set {exam.grading_rule_set_name}"
        )

    # 5. Check UniqueConstraint (exam_id, student_id)
    existing = await exams_service.get_result_by_exam_and_student(db, exam_id, payload.student_id)
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="RESULT_ALREADY_EXISTS",
            message="Result already exists for this student on this exam"
        )

    # 6. Store grade as computed string
    result = await exams_service.create_result(
        db,
        exam_id=exam_id,
        student_id=payload.student_id,
        entered_by=entered_by,
        marks_obtained=payload.marks_obtained,
        grade=grade
    )

    # 7. Write to audit_log
    await audit_service.log_action(
        db=db,
        actor_id=user.id,
        action=audit_service.RESULT_ENTERED,
        entity_type="exam_result",
        entity_id=result.id,
        new_value={
            "exam_id": str(exam.id),
            "student_id": str(payload.student_id),
            "marks_obtained": payload.marks_obtained,
            "grade": grade
        }
    )
    await db.commit()
    await db.refresh(result)

    data = ResultResponse(
        id=result.id,
        exam_id=result.exam_id,
        student_id=result.student_id,
        entered_by=result.entered_by,
        marks_obtained=result.marks_obtained,
        grade=result.grade,
        created_at=result.created_at
    ).model_dump()
    return success_response(data=data, message="Exam result recorded")

@router.put("/results/{result_id}")
@results_router.put("/{result_id}")
async def update_exam_result(
    result_id: uuid.UUID,
    payload: ResultUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_teacher)
):
    """Updates result, recomputes grade, writes audit log."""
    result = await exams_service.get_result_by_id(db, result_id)
    if not result:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="RESULT_NOT_FOUND",
            message="Result not found"
        )

    exam = await exams_service.get_exam_by_id(db, result.exam_id)
    if not exam:
        raise AppException(status_code=status.HTTP_404_NOT_FOUND, code="EXAM_NOT_FOUND", message="Exam not found")

    if user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        if not teacher or not await classes_service.is_teacher_assigned_to_student_subject(db, teacher.id, result.student_id, exam.subject_id):
            raise AppException(status_code=status.HTTP_403_FORBIDDEN, code="TEACHER_NOT_ASSIGNED", message="Not assigned")

    if payload.marks_obtained > exam.total_marks:
        raise AppException(status_code=status.HTTP_400_BAD_REQUEST, code="MARKS_EXCEED_TOTAL", message="Marks exceed total")
    if payload.marks_obtained < 0:
        raise AppException(status_code=status.HTTP_400_BAD_REQUEST, code="INVALID_MARKS", message="Marks cannot be negative")

    grade = await exams_service.compute_grade(db, exam.grading_rule_set_name, payload.marks_obtained)
    if not grade:
        raise AppException(status_code=status.HTTP_400_BAD_REQUEST, code="NO_MATCHING_GRADE_RULE", message="No rule matches")

    old_val = {"marks_obtained": result.marks_obtained, "grade": result.grade}
    result = await exams_service.update_result(db, result, payload.marks_obtained, grade)
    new_val = {"marks_obtained": result.marks_obtained, "grade": result.grade}

    await audit_service.log_action(
        db=db,
        actor_id=user.id,
        action=audit_service.RESULT_UPDATED,
        entity_type="exam_result",
        entity_id=result.id,
        old_value=old_val,
        new_value=new_val
    )
    await db.commit()
    await db.refresh(result)

    data = ResultResponse(
        id=result.id,
        exam_id=result.exam_id,
        student_id=result.student_id,
        entered_by=result.entered_by,
        marks_obtained=result.marks_obtained,
        grade=result.grade,
        created_at=result.created_at
    ).model_dump()
    return success_response(data=data, message="Result updated successfully")

