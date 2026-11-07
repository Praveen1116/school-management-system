import api from './axios'
import type { ApiSuccess, Student, ApiSuccessPaginated, ReportCard } from '../types'
import type { AxiosResponse } from 'axios'

export async function listStudents(params?: {
  page?: number
  limit?: number
  search?: string
  class_id?: string
}): Promise<AxiosResponse<ApiSuccessPaginated<Student>>> {
  return api.get('/api/students', { params })
}

export async function createStudent(data: {
  full_name: string
  roll_number: string
  date_of_birth: string
  guardian_id: string
}): Promise<AxiosResponse<ApiSuccess<Student>>> {
  return api.post('/api/students', data)
}

export async function getStudent(id: string): Promise<AxiosResponse<ApiSuccess<Student>>> {
  return api.get(`/api/students/${id}`)
}

export async function updateStudent(id: string, data: Partial<{
  full_name: string
  roll_number: string
  date_of_birth: string
  guardian_id: string
  is_active: boolean
}>): Promise<AxiosResponse<ApiSuccess<Student>>> {
  return api.put(`/api/students/${id}`, data)
}

export async function deleteStudent(id: string): Promise<AxiosResponse<ApiSuccess<{ message: string }>>> {
  return api.delete(`/api/students/${id}`)
}

export async function getReportCard(id: string): Promise<AxiosResponse<ApiSuccess<ReportCard>>> {
  return api.get(`/api/students/${id}/report-card`)
}

