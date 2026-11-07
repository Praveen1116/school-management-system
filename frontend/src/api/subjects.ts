import api from './axios'
import type { ApiSuccess, Subject } from '../types'
import type { AxiosResponse } from 'axios'

export async function listSubjects(): Promise<AxiosResponse<ApiSuccess<Subject[]>>> {
  return api.get('/api/subjects')
}

export async function createSubject(data: {
  name: string
  code: string
  total_marks: number
}): Promise<AxiosResponse<ApiSuccess<Subject>>> {
  return api.post('/api/subjects', data)
}

export async function updateSubject(id: string, data: Partial<{
  name: string
  code: string
  total_marks: number
}>): Promise<AxiosResponse<ApiSuccess<Subject>>> {
  return api.put(`/api/subjects/${id}`, data)
}

export async function deleteSubject(id: string): Promise<AxiosResponse<ApiSuccess<{ message: string }>>> {
  return api.delete(`/api/subjects/${id}`)
}

