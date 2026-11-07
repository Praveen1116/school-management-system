import api from './axios'
import type { ApiSuccess, Class, Student, Enrollment, ClassSubjectAssignment } from '../types'
import type { AxiosResponse } from 'axios'

export async function listClasses(): Promise<AxiosResponse<ApiSuccess<Class[]>>> {
  return api.get('/api/classes')
}

export async function createClass(data: {
  name: string
  section: string
  academic_year: number
}): Promise<AxiosResponse<ApiSuccess<Class>>> {
  return api.post('/api/classes', data)
}

export async function getClass(id: string): Promise<AxiosResponse<ApiSuccess<Class>>> {
  return api.get(`/api/classes/${id}`)
}

export async function updateClass(id: string, data: Partial<{
  name: string
  section: string
  academic_year: number
}>): Promise<AxiosResponse<ApiSuccess<Class>>> {
  return api.put(`/api/classes/${id}`, data)
}

export async function getClassStudents(id: string): Promise<AxiosResponse<ApiSuccess<Student[]>>> {
  return api.get(`/api/classes/${id}/students`)
}

export async function createEnrollment(data: {
  student_id: string
  class_id: string
  academic_year: number
}): Promise<AxiosResponse<ApiSuccess<Enrollment>>> {
  return api.post('/api/enrollments', data)
}

export async function deleteEnrollment(id: string): Promise<AxiosResponse<ApiSuccess<{ message: string }>>> {
  return api.delete(`/api/enrollments/${id}`)
}

export async function listAssignments(params?: {
  class_id?: string
  teacher_id?: string
}): Promise<AxiosResponse<ApiSuccess<ClassSubjectAssignment[]>>> {
  return api.get('/api/assignments', { params })
}

export async function createAssignment(data: {
  class_id: string
  subject_id: string
  teacher_id: string
  academic_year: number
}): Promise<AxiosResponse<ApiSuccess<ClassSubjectAssignment>>> {
  return api.post('/api/assignments', data)
}

export async function deleteAssignment(id: string): Promise<AxiosResponse<ApiSuccess<{ message: string }>>> {
  return api.delete(`/api/assignments/${id}`)
}

