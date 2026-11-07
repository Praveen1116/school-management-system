import api from './axios'
import type { ApiSuccess, ApiSuccessPaginated, DashboardStats, AuditLog } from '../types'
import type { AxiosResponse } from 'axios'

export async function getDashboard(): Promise<AxiosResponse<ApiSuccess<DashboardStats>>> {
  return api.get('/api/reports/dashboard')
}

export async function getAttendanceReport(params?: {
  class_id?: string
  date_from?: string
  date_to?: string
}): Promise<AxiosResponse<ApiSuccess<Record<string, unknown>>>> {
  return api.get('/api/reports/attendance', { params })
}

export async function getFeesReport(): Promise<AxiosResponse<ApiSuccess<Record<string, unknown>>>> {
  return api.get('/api/reports/fees')
}

export async function getAuditLogs(params?: {
  entity_type?: string
  date_from?: string
  date_to?: string
  page?: number
  limit?: number
}): Promise<AxiosResponse<ApiSuccessPaginated<AuditLog>>> {
  return api.get('/api/audit-logs', { params })
}

