import request from './request'
import type { ApiResponse, UserInfo } from '@/types'

export function login(data: { username: string; password: string }) {
  return request.post<ApiResponse<UserInfo>>('/api/auth/login', data)
}
