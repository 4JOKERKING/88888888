import request from './request'
import type { ApiResponse, DiagnosisRecord, PageResult } from '@/types'

export function uploadDiagnosis(formData: FormData) {
  return request.post<ApiResponse<DiagnosisRecord>>('/api/diagnosis/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function getDiagnosisList(params: {
  page?: number
  pageSize?: number
  keyword?: string
  status?: string
}) {
  return request.get<ApiResponse<PageResult<DiagnosisRecord>>>('/api/diagnosis', { params })
}

export function reviewDiagnosis(id: number, data: { action: 'APPROVE' | 'REJECT'; comment?: string; diseaseName?: string }) {
  return request.post<ApiResponse<DiagnosisRecord>>(`/api/diagnosis/${id}/review`, data)
}
