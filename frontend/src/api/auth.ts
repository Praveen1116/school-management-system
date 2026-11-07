import api from './axios'
import type { ApiSuccess, ApiSuccessPaginated, User } from '../types'
import type { AxiosResponse } from 'axios'

export async function login(email: string, password: string): Promise<AxiosResponse<ApiSuccess<{ access_token: string; token_type: string }>>> {
  return api.post('/api/auth/login', { email, password })
}

export async function getMe(): Promise<AxiosResponse<ApiSuccess<User>>> {
  return api.get('/api/auth/me')
}

export async function listUsers(params?: {
  role?: string
  page?: number
  limit?: number
}): Promise<AxiosResponse<ApiSuccessPaginated<User>>> {
  return api.get('/api/users', { params })
}

