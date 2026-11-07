import api from './axios'
import type { ApiSuccess, Exam, ExamResult, GradingRule } from '../types'
import type { AxiosResponse } from 'axios'

export async function listGradingRules(): Promise<AxiosResponse<ApiSuccess<GradingRule[]>>> {
  return api.get('/api/grading-rules')
}

export async function createGradingRule(data: {
  name: string
  grade_label: string
  min_marks: number
  max_marks: number
}): Promise<AxiosResponse<ApiSuccess<GradingRule>>> {
  return api.post('/api/grading-rules', data)
}

export async function listExams(): Promise<AxiosResponse<ApiSuccess<Exam[]>>> {
  return api.get('/api/exams')
}

export async function createExam(data: {
  subject_id: string
  grading_rule_set_name: string
  name: string
  total_marks: number
  exam_date: string
}): Promise<AxiosResponse<ApiSuccess<Exam>>> {
  return api.post('/api/exams', data)
}

export async function getExam(id: string): Promise<AxiosResponse<ApiSuccess<Exam>>> {
  return api.get(`/api/exams/${id}`)
}

export async function getExamResults(id: string): Promise<AxiosResponse<ApiSuccess<ExamResult[]>>> {
  return api.get(`/api/exams/${id}/results`)
}

export async function enterResult(examId: string, data: {
  student_id: string
  marks_obtained: number
}): Promise<AxiosResponse<ApiSuccess<ExamResult>>> {
  return api.post(`/api/exams/${examId}/results`, data)
}

export async function updateResult(id: string, data: {
  marks_obtained?: number
  grade?: string
}): Promise<AxiosResponse<ApiSuccess<ExamResult>>> {
  return api.put(`/api/results/${id}`, data)
}

