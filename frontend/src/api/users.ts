import api from './axios'
import type { ApiSuccess, ApiSuccessPaginated, User, CreateUserPayload } from '../types'
import type { AxiosResponse } from 'axios'

export async function listUsers(params?: {
  page?: number
  limit?: number
  role?: string
}): Promise<AxiosResponse<ApiSuccessPaginated<User>>> {
  return api.get('/api/users', { params })
}

export async function createUser(
  data: CreateUserPayload
): Promise<AxiosResponse<ApiSuccess<User>>> {
  return api.post('/api/users', data)
}

export async function getUser(id: string): Promise<AxiosResponse<ApiSuccess<User>>> {
  return api.get(`/api/users/${id}`)
}

export async function updateUser(
  id: string,
  data: Partial<{ email: string; role: string; full_name?: string }>
): Promise<AxiosResponse<ApiSuccess<User>>> {
  return api.put(`/api/users/${id}`, data)
}

export async function deleteUser(
  id: string
): Promise<AxiosResponse<ApiSuccess<{ id: string; is_active: boolean }>>> {
  return api.delete(`/api/users/${id}`)
}

