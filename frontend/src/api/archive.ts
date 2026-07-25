import request from './request'
import type { ApiResponse, FarmItem, FieldItem, CropItem } from '@/types'

export function getFarms() {
  return request.get<ApiResponse<FarmItem[]>>('/api/farms')
}
export function createFarm(data: Partial<FarmItem>) {
  return request.post<ApiResponse<FarmItem>>('/api/farms', data)
}
export function updateFarm(id: number, data: Partial<FarmItem>) {
  return request.put<ApiResponse<FarmItem>>(`/api/farms/${id}`, data)
}
export function deleteFarm(id: number) {
  return request.delete<ApiResponse<boolean>>(`/api/farms/${id}`)
}

export function getFields() {
  return request.get<ApiResponse<FieldItem[]>>('/api/fields')
}
export function createField(data: Partial<FieldItem>) {
  return request.post<ApiResponse<FieldItem>>('/api/fields', data)
}
export function updateField(id: number, data: Partial<FieldItem>) {
  return request.put<ApiResponse<FieldItem>>(`/api/fields/${id}`, data)
}
export function deleteField(id: number) {
  return request.delete<ApiResponse<boolean>>(`/api/fields/${id}`)
}

export function getCrops() {
  return request.get<ApiResponse<CropItem[]>>('/api/crops')
}
export function createCrop(data: Partial<CropItem>) {
  return request.post<ApiResponse<CropItem>>('/api/crops', data)
}
export function updateCrop(id: number, data: Partial<CropItem>) {
  return request.put<ApiResponse<CropItem>>(`/api/crops/${id}`, data)
}
export function deleteCrop(id: number) {
  return request.delete<ApiResponse<boolean>>(`/api/crops/${id}`)
}
