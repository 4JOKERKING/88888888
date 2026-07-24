import request from './request'
import type { ApiResponse, DashboardOverview } from '@/types'

export function getDashboardOverview() {
  return request.get<ApiResponse<DashboardOverview>>('/api/dashboard/overview')
}
