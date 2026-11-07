export interface User {
  id: string
  email: string
  role: 'admin' | 'teacher' | 'guardian'
  is_active: boolean
  created_at: string
  full_name?: string | null
}

export interface CreateUserPayload {
  email: string
  password: string
  role: 'admin' | 'teacher' | 'guardian'
  full_name?: string
}

export interface Student {
  id: string
  guardian_id: string
  guardian_name?: string
  full_name: string
  roll_number: string
  date_of_birth: string
  is_active: boolean
  created_at: string
}

export interface Teacher {
  id: string
  user_id: string
  full_name: string
  employee_code: string
  is_active: boolean
  email?: string
}

export interface Class {
  id: string
  name: string
  section: string
  academic_year: number
  studentCount?: number
}

export interface Subject {
  id: string
  name: string
  code: string
  total_marks: number
}

export interface Enrollment {
  id: string
  student_id: string
  class_id: string
  academic_year: number
}

export interface ClassSubjectAssignment {
  id: string
  class_id: string
  subject_id: string
  teacher_id: string
  academic_year: number
  class_name?: string
  section?: string
  subject_name?: string
  teacher_name?: string
}

export interface AttendanceRecord {
  id: string
  student_id: string
  student_name?: string
  roll_number?: string
  class_id: string
  recorded_by: string
  attendance_date: string
  session: 'full_day' | 'morning' | 'afternoon' | 'full-day' | string
  status: 'present' | 'absent' | 'late'
  created_at: string
}

export interface AttendanceSummary {
  total: number
  present: number
  absent: number
  late: number
  percentage?: number
  total_students?: number
  total_records?: number
  present_count?: number
  absent_count?: number
  late_count?: number
}

export interface AttendanceClassResponse {
  records: AttendanceRecord[]
  summary?: AttendanceSummary
}

export interface GradingRule {
  id: string
  name: string
  grade_label: string
  min_marks: number
  max_marks: number
}

export interface Exam {
  id: string
  subject_id: string
  subject_name?: string
  grading_rule_set_name: string
  name: string
  total_marks: number
  exam_date: string
}

export interface ExamResult {
  id: string
  exam_id: string
  student_id: string
  student_name?: string
  roll_number?: string
  entered_by: string
  marks_obtained: number
  grade: string
  created_at: string
  total_marks?: number
}

export interface ReportCardExam {
  exam_name: string
  exam_date?: string
  marks_obtained: number
  total_marks: number
  grade: string
}

export interface ReportCardSubject {
  subject_id?: string
  subject_name: string
  subject_code?: string
  exam_name?: string
  marks_obtained: number
  total_marks: number
  grade?: string
  exams?: ReportCardExam[]
}

export interface ReportCard {
  student: Student
  results: ReportCardSubject[]
  total_marks_obtained: number
  total_marks_possible: number
}

export interface FeeInvoice {
  id: string
  student_id: string
  student_name?: string
  description: string
  amount_due: number
  amount_paid?: number
  total_paid?: number
  balance?: number
  outstanding?: number
  status?: 'paid' | 'partial' | 'unpaid' | 'partially_paid'
  due_date: string
  created_at: string
}

export interface FeePayment {
  id: string
  invoice_id: string
  amount_paid: number
  payment_ref: string
  paid_at: string
}

export interface FeeBalance {
  invoice_id?: string
  amount_due: number
  total_paid: number
  outstanding: number
  status: 'paid' | 'partial' | 'unpaid'
}

export interface AuditLog {
  id: string
  actor_id: string
  actor_email: string
  action: string
  entity_type: string
  entity_id: string
  old_value: Record<string, unknown> | null
  new_value: Record<string, unknown> | null
  created_at: string
}

export interface DashboardStats {
  total_students: number
  total_teachers: number
  total_classes: number
  todays_attendance_rate: number
  total_fees_outstanding: number
  recent_audit_logs: AuditLog[]
}

export interface Pagination {
  page: number
  limit: number
  total: number
  pages: number
}

export interface ApiSuccess<T> {
  success: true
  data: T
  message: string
}

export interface ApiSuccessPaginated<T> {
  success: true
  data: T[]
  pagination: Pagination
  message?: string
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
  }
}

export interface SetupStatus {
  is_setup_required: boolean
  school_name?: string | null
  school_code?: string | null
}

export interface SetupPayload {
  school_name: string
  school_code: string
  full_name: string
  email: string
  password: string
}

export interface SetupResult {
  school_name: string
  school_code: string
  admin_email: string
  admin_name: string
}
