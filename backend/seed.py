import asyncio
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from sqlalchemy import select
from database import AsyncSessionLocal
from modules.auth.utils import hash_password
from modules.users.model import User
from modules.teachers.model import Teacher
from modules.students.model import Student
from modules.classes.model import Class, StudentClassEnrollment, ClassSubjectAssignment
from modules.subjects.model import Subject
from modules.exams.model import GradingRule, Exam, ExamResult
from modules.attendance.model import AttendanceRecord
from modules.fees.model import FeeInvoice, FeePayment
from modules.audit.model import AuditLog

async def seed_data():
    async with AsyncSessionLocal() as db:
        # Idempotency check: if admin@school.demo exists, skip seeding
        existing_admin = await db.execute(select(User).where(User.email == "admin@school.demo"))
        if existing_admin.scalar_one_or_none():
            print("Seed already run. Skipping.")
            return

        print("Seeding database...")

        # 1. USERS
        admin_user = User(email="admin@school.demo", password_hash=hash_password("Admin@123"), role="admin", is_active=True)
        teacher_a_user = User(email="teacher.a@school.demo", password_hash=hash_password("Teacher@123"), role="teacher", is_active=True)
        teacher_b_user = User(email="teacher.b@school.demo", password_hash=hash_password("Teacher@123"), role="teacher", is_active=True)
        guardian_a_user = User(email="guardian.a@school.demo", password_hash=hash_password("Guardian@123"), role="guardian", is_active=True)
        guardian_b_user = User(email="guardian.b@school.demo", password_hash=hash_password("Guardian@123"), role="guardian", is_active=True)

        db.add_all([admin_user, teacher_a_user, teacher_b_user, guardian_a_user, guardian_b_user])
        await db.flush()

        # 2. TEACHERS
        teacher_amit = Teacher(user_id=teacher_a_user.id, full_name="Amit Verma", employee_code="TCH001", is_active=True)
        teacher_sunita = Teacher(user_id=teacher_b_user.id, full_name="Sunita Rao", employee_code="TCH002", is_active=True)

        db.add_all([teacher_amit, teacher_sunita])
        await db.flush()

        # 3. STUDENTS (linked to guardians)
        ravi = Student(guardian_id=guardian_a_user.id, full_name="Ravi Sharma", roll_number="STU001", date_of_birth=date(2009, 6, 15), is_active=True)
        priya = Student(guardian_id=guardian_b_user.id, full_name="Priya Mehta", roll_number="STU002", date_of_birth=date(2009, 11, 20), is_active=True)
        arjun = Student(guardian_id=guardian_a_user.id, full_name="Arjun Singh", roll_number="STU003", date_of_birth=date(2010, 3, 8), is_active=True)
        sneha = Student(guardian_id=guardian_b_user.id, full_name="Sneha Patel", roll_number="STU004", date_of_birth=date(2009, 8, 25), is_active=True)
        rahul = Student(guardian_id=guardian_a_user.id, full_name="Rahul Das", roll_number="STU005", date_of_birth=date(2010, 1, 12), is_active=True)

        db.add_all([ravi, priya, arjun, sneha, rahul])
        await db.flush()

        # 4. CLASSES
        c10a = Class(name="Class 10", section="A", academic_year=2026)
        c10b = Class(name="Class 10", section="B", academic_year=2026)
        c11a = Class(name="Class 11", section="A", academic_year=2026)

        db.add_all([c10a, c10b, c11a])
        await db.flush()

        # 5. SUBJECTS
        math = Subject(name="Mathematics", code="MATH", total_marks=100)
        sci = Subject(name="Science", code="SCI", total_marks=100)
        eng = Subject(name="English", code="ENG", total_marks=100)
        hist = Subject(name="History", code="HIST", total_marks=100)

        db.add_all([math, sci, eng, hist])
        await db.flush()

        # 6. ENROLLMENTS
        e1 = StudentClassEnrollment(student_id=ravi.id, class_id=c10a.id, academic_year=2026)
        e2 = StudentClassEnrollment(student_id=arjun.id, class_id=c10a.id, academic_year=2026)
        e3 = StudentClassEnrollment(student_id=rahul.id, class_id=c10a.id, academic_year=2026)
        e4 = StudentClassEnrollment(student_id=priya.id, class_id=c10b.id, academic_year=2026)
        e5 = StudentClassEnrollment(student_id=sneha.id, class_id=c10b.id, academic_year=2026)

        db.add_all([e1, e2, e3, e4, e5])
        await db.flush()

        # 7. CLASS-SUBJECT-TEACHER ASSIGNMENTS
        a1 = ClassSubjectAssignment(class_id=c10a.id, subject_id=math.id, teacher_id=teacher_amit.id, academic_year=2026)
        a2 = ClassSubjectAssignment(class_id=c10a.id, subject_id=sci.id, teacher_id=teacher_amit.id, academic_year=2026)
        a3 = ClassSubjectAssignment(class_id=c10b.id, subject_id=eng.id, teacher_id=teacher_sunita.id, academic_year=2026)

        db.add_all([a1, a2, a3])
        await db.flush()

        # 8. GRADING RULES ("Standard 2026")
        gr_a = GradingRule(name="Standard 2026", grade_label="A", min_marks=90, max_marks=100)
        gr_b = GradingRule(name="Standard 2026", grade_label="B", min_marks=75, max_marks=89)
        gr_c = GradingRule(name="Standard 2026", grade_label="C", min_marks=60, max_marks=74)
        gr_d = GradingRule(name="Standard 2026", grade_label="D", min_marks=45, max_marks=59)
        gr_f = GradingRule(name="Standard 2026", grade_label="F", min_marks=0, max_marks=44)

        db.add_all([gr_a, gr_b, gr_c, gr_d, gr_f])
        await db.flush()

        # 9. EXAMS
        exam_math = Exam(
            subject_id=math.id,
            grading_rule_set_name="Standard 2026",
            name="Mathematics Midterm",
            total_marks=100,
            exam_date=date(2026, 10, 1)
        )
        db.add(exam_math)
        await db.flush()

        # 10. EXAM RESULTS
        r1 = ExamResult(exam_id=exam_math.id, student_id=ravi.id, entered_by=teacher_amit.id, marks_obtained=92, grade="A")
        r2 = ExamResult(exam_id=exam_math.id, student_id=arjun.id, entered_by=teacher_amit.id, marks_obtained=78, grade="B")
        r3 = ExamResult(exam_id=exam_math.id, student_id=rahul.id, entered_by=teacher_amit.id, marks_obtained=61, grade="C")

        db.add_all([r1, r2, r3])
        await db.flush()

        # 11. ATTENDANCE RECORDS (Past 7 days for Class 10A)
        today = date.today()
        # Days 1 to 6 before today
        for offset in range(6, 0, -1):
            att_date = today - timedelta(days=offset)
            # Ravi has 1 absent (on offset 3)
            ravi_status = "absent" if offset == 3 else "present"
            # Arjun has 2 absents (on offset 2 and 4)
            arjun_status = "absent" if offset in (2, 4) else "present"
            rahul_status = "present"

            db.add_all([
                AttendanceRecord(student_id=ravi.id, class_id=c10a.id, recorded_by=teacher_amit.id, attendance_date=att_date, session="full_day", status=ravi_status),
                AttendanceRecord(student_id=arjun.id, class_id=c10a.id, recorded_by=teacher_amit.id, attendance_date=att_date, session="full_day", status=arjun_status),
                AttendanceRecord(student_id=rahul.id, class_id=c10a.id, recorded_by=teacher_amit.id, attendance_date=att_date, session="full_day", status=rahul_status),
            ])

        # Record for TODAY for Ravi Sharma (to test duplicate rejection)
        db.add(AttendanceRecord(student_id=ravi.id, class_id=c10a.id, recorded_by=teacher_amit.id, attendance_date=today, session="full_day", status="present"))
        await db.flush()

        # 12. FEE INVOICES AND PAYMENTS
        inv_ravi = FeeInvoice(student_id=ravi.id, description="Tuition Fee Term 1", amount_due=500000, due_date=date(2026, 11, 30))
        inv_priya = FeeInvoice(student_id=priya.id, description="Tuition Fee Term 1", amount_due=500000, due_date=date(2026, 11, 30))
        inv_rahul = FeeInvoice(student_id=rahul.id, description="Tuition Fee Term 1", amount_due=500000, due_date=date(2026, 11, 30))

        db.add_all([inv_ravi, inv_priya, inv_rahul])
        await db.flush()

        pay_ravi = FeePayment(invoice_id=inv_ravi.id, amount_paid=200000, payment_ref="PAY001")
        pay_priya1 = FeePayment(invoice_id=inv_priya.id, amount_paid=300000, payment_ref="PAY002")
        pay_priya2 = FeePayment(invoice_id=inv_priya.id, amount_paid=200000, payment_ref="PAY003")

        db.add_all([pay_ravi, pay_priya1, pay_priya2])
        await db.flush()

        # 13. AUDIT LOGS (10 realistic entries)
        db.add_all([
            AuditLog(actor_id=admin_user.id, action="STUDENT_CREATED", entity_type="student", entity_id=ravi.id, new_value={"full_name": "Ravi Sharma", "roll": "STU001"}),
            AuditLog(actor_id=admin_user.id, action="STUDENT_CREATED", entity_type="student", entity_id=priya.id, new_value={"full_name": "Priya Mehta", "roll": "STU002"}),
            AuditLog(actor_id=teacher_a_user.id, action="ATTENDANCE_RECORDED", entity_type="attendance", entity_id=ravi.id, new_value={"date": str(today), "status": "present"}),
            AuditLog(actor_id=teacher_a_user.id, action="RESULT_ENTERED", entity_type="exam_result", entity_id=r1.id, new_value={"exam": "Maths", "marks": 92, "grade": "A"}),
            AuditLog(actor_id=admin_user.id, action="PAYMENT_RECORDED", entity_type="fee_payment", entity_id=pay_ravi.id, new_value={"ref": "PAY001", "amount": 200000}),
            AuditLog(actor_id=admin_user.id, action="PAYMENT_RECORDED", entity_type="fee_payment", entity_id=pay_priya1.id, new_value={"ref": "PAY002", "amount": 300000}),
            AuditLog(actor_id=admin_user.id, action="PAYMENT_RECORDED", entity_type="fee_payment", entity_id=pay_priya2.id, new_value={"ref": "PAY003", "amount": 200000}),
            AuditLog(actor_id=teacher_a_user.id, action="ATTENDANCE_RECORDED", entity_type="attendance", entity_id=arjun.id, new_value={"student": "Arjun Singh", "status": "present"}),
            AuditLog(actor_id=teacher_a_user.id, action="RESULT_ENTERED", entity_type="exam_result", entity_id=r2.id, new_value={"exam": "Maths", "marks": 78, "grade": "B"}),
            AuditLog(actor_id=admin_user.id, action="STUDENT_CREATED", entity_type="student", entity_id=rahul.id, new_value={"full_name": "Rahul Das", "roll": "STU005"}),
        ])

        await db.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())

