import request from './request'
import type { ApiResponse, ModelMonitor } from '@/types'

export function getModelMonitor() {
  return request.get<ApiResponse<ModelMonitor>>('/api/monitor/model')
}
