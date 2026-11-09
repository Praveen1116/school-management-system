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
from modules.setup.model import School
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

        print("Seeding database with full production demo dataset...")

        # 0. SCHOOL
        school = School(school_name="Demo Public School", school_code="DPS-01")
        db.add(school)
        await db.flush()

        # 1. USERS (1 Admin + 3 Teachers + 5 Guardians)
        admin_user = User(
            email="admin@school.demo",
            password_hash=hash_password("Admin@123"),
            role="admin",
            full_name="System Administrator",
            is_active=True
        )
        teacher_a_user = User(
            email="teacher.a@school.demo",
            password_hash=hash_password("Teacher@123"),
            role="teacher",
            full_name="Amit Verma",
            is_active=True
        )
        teacher_b_user = User(
            email="teacher.b@school.demo",
            password_hash=hash_password("Teacher@123"),
            role="teacher",
            full_name="Sunita Rao",
            is_active=True
        )
        teacher_c_user = User(
            email="teacher.c@school.demo",
            password_hash=hash_password("Teacher@123"),
            role="teacher",
            full_name="Ramesh Gupta",
            is_active=True
        )
        guardian_a_user = User(
            email="guardian.a@school.demo",
            password_hash=hash_password("Guardian@123"),
            role="guardian",
            full_name="Rajesh Sharma",
            is_active=True
        )
        guardian_b_user = User(
            email="guardian.b@school.demo",
            password_hash=hash_password("Guardian@123"),
            role="guardian",
            full_name="Vikram Mehta",
            is_active=True
        )
        guardian_c_user = User(
            email="guardian.c@school.demo",
            password_hash=hash_password("Guardian@123"),
            role="guardian",
            full_name="Sanjay Verma",
            is_active=True
        )
        guardian_d_user = User(
            email="guardian.d@school.demo",
            password_hash=hash_password("Guardian@123"),
            role="guardian",
            full_name="Anil Kapoor",
            is_active=True
        )
        guardian_e_user = User(
            email="guardian.e@school.demo",
            password_hash=hash_password("Guardian@123"),
            role="guardian",
            full_name="Sunil Joshi",
            is_active=True
        )

        db.add_all([
            admin_user,
            teacher_a_user, teacher_b_user, teacher_c_user,
            guardian_a_user, guardian_b_user, guardian_c_user, guardian_d_user, guardian_e_user
        ])
        await db.flush()

        # 2. TEACHERS (3 Teachers)
        teacher_amit = Teacher(user_id=teacher_a_user.id, full_name="Amit Verma", employee_code="TCH001", is_active=True)
        teacher_sunita = Teacher(user_id=teacher_b_user.id, full_name="Sunita Rao", employee_code="TCH002", is_active=True)
        teacher_ramesh = Teacher(user_id=teacher_c_user.id, full_name="Ramesh Gupta", employee_code="TCH003", is_active=True)

        db.add_all([teacher_amit, teacher_sunita, teacher_ramesh])
        await db.flush()

        # 3. STUDENTS (12 Students across 5 Guardians)
        # Guardian A (Rajesh Sharma)
        ravi = Student(guardian_id=guardian_a_user.id, full_name="Ravi Sharma", roll_number="STU001", date_of_birth=date(2009, 6, 15), is_active=True)
        arjun = Student(guardian_id=guardian_a_user.id, full_name="Arjun Singh", roll_number="STU003", date_of_birth=date(2010, 3, 8), is_active=True)
        rahul = Student(guardian_id=guardian_a_user.id, full_name="Rahul Das", roll_number="STU005", date_of_birth=date(2010, 1, 12), is_active=True)

        # Guardian B (Vikram Mehta)
        priya = Student(guardian_id=guardian_b_user.id, full_name="Priya Mehta", roll_number="STU002", date_of_birth=date(2009, 11, 20), is_active=True)
        sneha = Student(guardian_id=guardian_b_user.id, full_name="Sneha Patel", roll_number="STU004", date_of_birth=date(2009, 8, 25), is_active=True)

        # Guardian C (Sanjay Verma)
        aditi = Student(guardian_id=guardian_c_user.id, full_name="Aditi Verma", roll_number="STU006", date_of_birth=date(2010, 4, 18), is_active=True)
        rohan = Student(guardian_id=guardian_c_user.id, full_name="Rohan Verma", roll_number="STU007", date_of_birth=date(2009, 9, 5), is_active=True)

        # Guardian D (Anil Kapoor)
        kavya = Student(guardian_id=guardian_d_user.id, full_name="Kavya Kapoor", roll_number="STU008", date_of_birth=date(2010, 2, 14), is_active=True)
        vihaan = Student(guardian_id=guardian_d_user.id, full_name="Vihaan Kapoor", roll_number="STU009", date_of_birth=date(2009, 7, 22), is_active=True)
        ananya = Student(guardian_id=guardian_d_user.id, full_name="Ananya Kapoor", roll_number="STU010", date_of_birth=date(2008, 12, 10), is_active=True)

        # Guardian E (Sunil Joshi)
        ishaan = Student(guardian_id=guardian_e_user.id, full_name="Ishaan Joshi", roll_number="STU011", date_of_birth=date(2008, 10, 30), is_active=True)
        diya = Student(guardian_id=guardian_e_user.id, full_name="Diya Joshi", roll_number="STU012", date_of_birth=date(2008, 5, 19), is_active=True)

        db.add_all([ravi, priya, arjun, sneha, rahul, aditi, rohan, kavya, vihaan, ananya, ishaan, diya])
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
        # Class 10A: 5 students
        e1 = StudentClassEnrollment(student_id=ravi.id, class_id=c10a.id, academic_year=2026)
        e2 = StudentClassEnrollment(student_id=arjun.id, class_id=c10a.id, academic_year=2026)
        e3 = StudentClassEnrollment(student_id=rahul.id, class_id=c10a.id, academic_year=2026)
        e4 = StudentClassEnrollment(student_id=aditi.id, class_id=c10a.id, academic_year=2026)
        e5 = StudentClassEnrollment(student_id=kavya.id, class_id=c10a.id, academic_year=2026)

        # Class 10B: 4 students
        e6 = StudentClassEnrollment(student_id=priya.id, class_id=c10b.id, academic_year=2026)
        e7 = StudentClassEnrollment(student_id=sneha.id, class_id=c10b.id, academic_year=2026)
        e8 = StudentClassEnrollment(student_id=rohan.id, class_id=c10b.id, academic_year=2026)
        e9 = StudentClassEnrollment(student_id=vihaan.id, class_id=c10b.id, academic_year=2026)

        # Class 11A: 3 students
        e10 = StudentClassEnrollment(student_id=ananya.id, class_id=c11a.id, academic_year=2026)
        e11 = StudentClassEnrollment(student_id=ishaan.id, class_id=c11a.id, academic_year=2026)
        e12 = StudentClassEnrollment(student_id=diya.id, class_id=c11a.id, academic_year=2026)

        db.add_all([e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11, e12])
        await db.flush()

        # 7. CLASS-SUBJECT-TEACHER ASSIGNMENTS
        a1 = ClassSubjectAssignment(class_id=c10a.id, subject_id=math.id, teacher_id=teacher_amit.id, academic_year=2026)
        a2 = ClassSubjectAssignment(class_id=c10a.id, subject_id=sci.id, teacher_id=teacher_amit.id, academic_year=2026)
        a3 = ClassSubjectAssignment(class_id=c10b.id, subject_id=eng.id, teacher_id=teacher_sunita.id, academic_year=2026)
        a4 = ClassSubjectAssignment(class_id=c10a.id, subject_id=hist.id, teacher_id=teacher_ramesh.id, academic_year=2026)
        a5 = ClassSubjectAssignment(class_id=c10b.id, subject_id=hist.id, teacher_id=teacher_ramesh.id, academic_year=2026)
        a6 = ClassSubjectAssignment(class_id=c11a.id, subject_id=eng.id, teacher_id=teacher_sunita.id, academic_year=2026)
        a7 = ClassSubjectAssignment(class_id=c11a.id, subject_id=math.id, teacher_id=teacher_amit.id, academic_year=2026)

        db.add_all([a1, a2, a3, a4, a5, a6, a7])
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
        exam_eng = Exam(
            subject_id=eng.id,
            grading_rule_set_name="Standard 2026",
            name="English Midterm",
            total_marks=100,
            exam_date=date(2026, 10, 5)
        )
        db.add_all([exam_math, exam_eng])
        await db.flush()

        # 10. EXAM RESULTS
        # Math Results
        r1 = ExamResult(exam_id=exam_math.id, student_id=ravi.id, entered_by=teacher_amit.id, marks_obtained=92, grade="A")
        r2 = ExamResult(exam_id=exam_math.id, student_id=arjun.id, entered_by=teacher_amit.id, marks_obtained=78, grade="B")
        r3 = ExamResult(exam_id=exam_math.id, student_id=rahul.id, entered_by=teacher_amit.id, marks_obtained=61, grade="C")
        r4 = ExamResult(exam_id=exam_math.id, student_id=aditi.id, entered_by=teacher_amit.id, marks_obtained=95, grade="A")
        r5 = ExamResult(exam_id=exam_math.id, student_id=kavya.id, entered_by=teacher_amit.id, marks_obtained=84, grade="B")

        # English Results
        r6 = ExamResult(exam_id=exam_eng.id, student_id=priya.id, entered_by=teacher_sunita.id, marks_obtained=88, grade="B")
        r7 = ExamResult(exam_id=exam_eng.id, student_id=sneha.id, entered_by=teacher_sunita.id, marks_obtained=94, grade="A")
        r8 = ExamResult(exam_id=exam_eng.id, student_id=rohan.id, entered_by=teacher_sunita.id, marks_obtained=72, grade="C")
        r9 = ExamResult(exam_id=exam_eng.id, student_id=vihaan.id, entered_by=teacher_sunita.id, marks_obtained=81, grade="B")

        db.add_all([r1, r2, r3, r4, r5, r6, r7, r8, r9])
        await db.flush()

        # 11. ATTENDANCE RECORDS (Past 7 days for Class 10A & 10B)
        today = date.today()
        attendance_batch = []
        for offset in range(6, 0, -1):
            att_date = today - timedelta(days=offset)
            # Class 10A
            attendance_batch.extend([
                AttendanceRecord(student_id=ravi.id, class_id=c10a.id, recorded_by=teacher_amit.id, attendance_date=att_date, session="full_day", status="absent" if offset == 3 else "present"),
                AttendanceRecord(student_id=arjun.id, class_id=c10a.id, recorded_by=teacher_amit.id, attendance_date=att_date, session="full_day", status="absent" if offset in (2, 4) else "present"),
                AttendanceRecord(student_id=rahul.id, class_id=c10a.id, recorded_by=teacher_amit.id, attendance_date=att_date, session="full_day", status="present"),
                AttendanceRecord(student_id=aditi.id, class_id=c10a.id, recorded_by=teacher_amit.id, attendance_date=att_date, session="full_day", status="present"),
                AttendanceRecord(student_id=kavya.id, class_id=c10a.id, recorded_by=teacher_amit.id, attendance_date=att_date, session="full_day", status="late" if offset == 1 else "present"),
            ])
            # Class 10B
            attendance_batch.extend([
                AttendanceRecord(student_id=priya.id, class_id=c10b.id, recorded_by=teacher_sunita.id, attendance_date=att_date, session="full_day", status="present"),
                AttendanceRecord(student_id=sneha.id, class_id=c10b.id, recorded_by=teacher_sunita.id, attendance_date=att_date, session="full_day", status="present"),
                AttendanceRecord(student_id=rohan.id, class_id=c10b.id, recorded_by=teacher_sunita.id, attendance_date=att_date, session="full_day", status="absent" if offset == 5 else "present"),
                AttendanceRecord(student_id=vihaan.id, class_id=c10b.id, recorded_by=teacher_sunita.id, attendance_date=att_date, session="full_day", status="present"),
            ])

        # Record for TODAY for Ravi Sharma (for duplicate rejection testing)
        attendance_batch.append(
            AttendanceRecord(student_id=ravi.id, class_id=c10a.id, recorded_by=teacher_amit.id, attendance_date=today, session="full_day", status="present")
        )
        db.add_all(attendance_batch)
        await db.flush()

        # 12. FEE INVOICES AND PAYMENTS
        inv_ravi = FeeInvoice(student_id=ravi.id, description="Tuition Fee Term 1", amount_due=500000, due_date=date(2026, 11, 30))
        inv_priya = FeeInvoice(student_id=priya.id, description="Tuition Fee Term 1", amount_due=500000, due_date=date(2026, 11, 30))
        inv_rahul = FeeInvoice(student_id=rahul.id, description="Tuition Fee Term 1", amount_due=500000, due_date=date(2026, 11, 30))
        inv_aditi = FeeInvoice(student_id=aditi.id, description="Tuition Fee Term 1", amount_due=500000, due_date=date(2026, 11, 30))
        inv_kavya = FeeInvoice(student_id=kavya.id, description="Tuition Fee Term 1", amount_due=500000, due_date=date(2026, 11, 30))
        inv_ananya = FeeInvoice(student_id=ananya.id, description="Annual Fee 2026", amount_due=600000, due_date=date(2026, 12, 15))
        inv_ishaan = FeeInvoice(student_id=ishaan.id, description="Annual Fee 2026", amount_due=600000, due_date=date(2026, 12, 15))

        db.add_all([inv_ravi, inv_priya, inv_rahul, inv_aditi, inv_kavya, inv_ananya, inv_ishaan])
        await db.flush()

        # Payments:
        # Ravi: 2,000 paid / 5,000 (Partial, 3,000 due)
        pay_ravi = FeePayment(invoice_id=inv_ravi.id, amount_paid=200000, payment_ref="PAY001")
        # Priya: 5,000 paid / 5,000 (Fully Paid)
        pay_priya1 = FeePayment(invoice_id=inv_priya.id, amount_paid=300000, payment_ref="PAY002")
        pay_priya2 = FeePayment(invoice_id=inv_priya.id, amount_paid=200000, payment_ref="PAY003")
        # Aditi: 2,500 paid / 5,000 (Partial, 2,500 due)
        pay_aditi = FeePayment(invoice_id=inv_aditi.id, amount_paid=250000, payment_ref="PAY004")
        # Kavya: 5,000 paid / 5,000 (Fully Paid)
        pay_kavya = FeePayment(invoice_id=inv_kavya.id, amount_paid=500000, payment_ref="PAY005")
        # Ananya: 3,000 paid / 6,000 (Partial, 3,000 due)
        pay_ananya = FeePayment(invoice_id=inv_ananya.id, amount_paid=300000, payment_ref="PAY006")
        # Rahul & Ishaan: No payments (Unpaid)

        db.add_all([pay_ravi, pay_priya1, pay_priya2, pay_aditi, pay_kavya, pay_ananya])
        await db.flush()

        # 13. AUDIT LOGS (Real tracking of administrative events)
        db.add_all([
            AuditLog(actor_id=admin_user.id, action="STUDENT_CREATED", entity_type="student", entity_id=ravi.id, new_value={"full_name": "Ravi Sharma", "roll": "STU001"}),
            AuditLog(actor_id=admin_user.id, action="STUDENT_CREATED", entity_type="student", entity_id=priya.id, new_value={"full_name": "Priya Mehta", "roll": "STU002"}),
            AuditLog(actor_id=admin_user.id, action="STUDENT_CREATED", entity_type="student", entity_id=aditi.id, new_value={"full_name": "Aditi Verma", "roll": "STU006"}),
            AuditLog(actor_id=admin_user.id, action="TEACHER_CREATED", entity_type="teacher", entity_id=teacher_ramesh.id, new_value={"full_name": "Ramesh Gupta", "code": "TCH003"}),
            AuditLog(actor_id=teacher_a_user.id, action="ATTENDANCE_RECORDED", entity_type="attendance", entity_id=ravi.id, new_value={"date": str(today), "status": "present"}),
            AuditLog(actor_id=teacher_a_user.id, action="RESULT_ENTERED", entity_type="exam_result", entity_id=r1.id, new_value={"exam": "Maths", "marks": 92, "grade": "A"}),
            AuditLog(actor_id=teacher_b_user.id, action="RESULT_ENTERED", entity_type="exam_result", entity_id=r6.id, new_value={"exam": "English", "marks": 88, "grade": "B"}),
            AuditLog(actor_id=admin_user.id, action="PAYMENT_RECORDED", entity_type="fee_payment", entity_id=pay_ravi.id, new_value={"ref": "PAY001", "amount": 200000}),
            AuditLog(actor_id=admin_user.id, action="PAYMENT_RECORDED", entity_type="fee_payment", entity_id=pay_priya1.id, new_value={"ref": "PAY002", "amount": 300000}),
            AuditLog(actor_id=admin_user.id, action="PAYMENT_RECORDED", entity_type="fee_payment", entity_id=pay_kavya.id, new_value={"ref": "PAY005", "amount": 500000}),
            AuditLog(actor_id=admin_user.id, action="PAYMENT_RECORDED", entity_type="fee_payment", entity_id=pay_ananya.id, new_value={"ref": "PAY006", "amount": 300000}),
        ])

        await db.commit()
        print("Database seeded with 12 students, 3 teachers, and 5 guardians successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
