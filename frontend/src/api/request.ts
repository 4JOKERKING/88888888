import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'
import { useMock } from '@/api/mock'

const useMockMode = import.meta.env.VITE_USE_MOCK === 'true'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '',
  timeout: 60000
})

if (useMockMode) {
  request.defaults.adapter = async (config) => {
    const mocked = await useMock(config)
    if (!mocked) {
      throw new Error(`未实现的 Mock 接口: ${config.method} ${config.url}`)
    }
    return mocked
  }
}

request.interceptors.request.use((config) => {
  const raw = localStorage.getItem('agri_user')
  if (raw) {
    const user = JSON.parse(raw)
    if (user.token) {
      config.headers.Authorization = `Bearer ${user.token}`
    }
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const body = response.data as ApiResponse<unknown>
    if (body && typeof body.code === 'number' && body.code !== 200) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(new Error(body.message || '请求失败'))
    }
    return response
  },
  (error) => {
    ElMessage.error(error.response?.data?.message || error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
