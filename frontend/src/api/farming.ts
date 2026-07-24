import request from './request'
import type { ApiResponse, FarmingTask } from '@/types'

export function getFarmingTasks() {
  return request.get<ApiResponse<FarmingTask[]>>('/api/farming-tasks')
}

export function createFarmingTask(data: Partial<FarmingTask>) {
  return request.post<ApiResponse<FarmingTask>>('/api/farming-tasks', data)
}

export function updateFarmingTask(id: number, data: Partial<FarmingTask>) {
  return request.put<ApiResponse<FarmingTask>>(`/api/farming-tasks/${id}`, data)
}
