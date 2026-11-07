import api from './axios'
import type { ApiSuccess, ApiSuccessPaginated, Teacher } from '../types'
import type { AxiosResponse } from 'axios'

export async function listTeachers(params?: {
  page?: number
  limit?: number
}): Promise<AxiosResponse<ApiSuccessPaginated<Teacher>>> {
  return api.get('/api/teachers', { params })
}

export async function createTeacher(data: {
  full_name: string
  employee_code: string
  email: string
  password?: string
}): Promise<AxiosResponse<ApiSuccess<Teacher>>> {
  return api.post('/api/teachers', data)
}

export async function getTeacher(id: string): Promise<AxiosResponse<ApiSuccess<Teacher>>> {
  return api.get(`/api/teachers/${id}`)
}

export async function updateTeacher(id: string, data: Partial<{
  full_name: string
  employee_code: string
  is_active: boolean
}>): Promise<AxiosResponse<ApiSuccess<Teacher>>> {
  return api.put(`/api/teachers/${id}`, data)
}

export async function deleteTeacher(id: string): Promise<AxiosResponse<ApiSuccess<{ message: string }>>> {
  return api.delete(`/api/teachers/${id}`)
}

