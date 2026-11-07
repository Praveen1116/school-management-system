import api from './axios'
import type { ApiSuccess, Student, AttendanceRecord, AttendanceSummary, ReportCardSubject, FeeInvoice } from '../types'
import type { AxiosResponse } from 'axios'

export async function getMyStudents(): Promise<AxiosResponse<ApiSuccess<Student[]>>> {
  return api.get('/api/guardian/me/students')
}

export async function getStudentAttendance(studentId: string, params: {
  date_from: string
  date_to: string
}): Promise<AxiosResponse<ApiSuccess<{ records: AttendanceRecord[]; summary: AttendanceSummary }>>> {
  return api.get(`/api/guardian/me/students/${studentId}/attendance`, { params })
}

export async function getStudentReportCard(studentId: string): Promise<AxiosResponse<ApiSuccess<ReportCardSubject[]>>> {
  return api.get(`/api/guardian/me/students/${studentId}/report-card`)
}

export async function getStudentFeeSummary(studentId: string): Promise<AxiosResponse<ApiSuccess<FeeInvoice[]>>> {
  return api.get(`/api/guardian/me/students/${studentId}/fee-summary`)
}
