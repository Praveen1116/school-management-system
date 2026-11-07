import api from './axios'
import type { ApiSuccess, FeeInvoice, FeePayment, FeeBalance } from '../types'
import type { AxiosResponse } from 'axios'

export async function listInvoices(params?: {
  student_id?: string
}): Promise<AxiosResponse<ApiSuccess<FeeInvoice[]>>> {
  return api.get('/api/fees/invoices', { params })
}

export async function createInvoice(data: {
  student_id: string
  description: string
  amount_due: number
  due_date: string
}): Promise<AxiosResponse<ApiSuccess<FeeInvoice>>> {
  return api.post('/api/fees/invoices', data)
}

export async function getInvoice(id: string): Promise<AxiosResponse<ApiSuccess<FeeInvoice>>> {
  return api.get(`/api/fees/invoices/${id}`)
}

export async function updateInvoice(id: string, data: Partial<{
  description: string
  amount_due: number
  due_date: string
}>): Promise<AxiosResponse<ApiSuccess<FeeInvoice>>> {
  return api.put(`/api/fees/invoices/${id}`, data)
}

export async function getInvoicePayments(id: string): Promise<AxiosResponse<ApiSuccess<FeePayment[]>>> {
  return api.get(`/api/fees/invoices/${id}/payments`)
}

export async function recordPayment(invoiceId: string, data: {
  amount_paid: number
  payment_ref: string
}): Promise<AxiosResponse<ApiSuccess<{ payment: FeePayment; balance: FeeBalance }>>> {
  return api.post(`/api/fees/invoices/${invoiceId}/payments`, data)
}

export async function getBalance(id: string): Promise<AxiosResponse<ApiSuccess<FeeBalance>>> {
  return api.get(`/api/fees/invoices/${id}/balance`)
}

export async function getStudentFeeSummary(studentId: string): Promise<AxiosResponse<ApiSuccess<FeeInvoice[]>>> {
  return api.get(`/api/students/${studentId}/fee-summary`)
}

