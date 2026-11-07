import api from './axios'
import type { ApiSuccess, AttendanceRecord, AttendanceClassResponse, AttendanceSummary } from '../types'
import type { AxiosResponse } from 'axios'

export async function recordAttendance(data: {
  student_id: string
  class_id: string
  attendance_date: string
  session: string
  status: string
}): Promise<AxiosResponse<ApiSuccess<AttendanceRecord>>> {
  return api.post('/api/attendance', data)
}

export async function updateAttendance(id: string, data: {
  status: string
  session?: string
}): Promise<AxiosResponse<ApiSuccess<AttendanceRecord>>> {
  return api.put(`/api/attendance/${id}`, data)
}

export async function getClassAttendance(classId: string, params: {
  date_from: string
  date_to: string
}): Promise<AxiosResponse<ApiSuccess<AttendanceClassResponse>>> {
  return api.get(`/api/attendance/class/${classId}`, { params })
}

export async function getStudentAttendance(studentId: string, params: {
  date_from: string
  date_to: string
}): Promise<AxiosResponse<ApiSuccess<{ records: AttendanceRecord[]; summary: AttendanceSummary }>>> {
  return api.get(`/api/attendance/student/${studentId}`, { params })
}

