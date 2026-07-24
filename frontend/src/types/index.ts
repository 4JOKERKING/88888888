export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export type UserRole = 'FARMER' | 'TECH' | 'COOP' | 'ADMIN'

export interface UserInfo {
  token: string
  userId: number
  username: string
  nickname: string
  role: UserRole
}

export interface FarmItem {
  id: number
  name: string
  ownerName: string
  location: string
  area: number
  status: string
}

export interface FieldItem {
  id: number
  farmId: number
  farmName?: string
  name: string
  area: number
  location: string
  status: string
}

export interface CropItem {
  id: number
  fieldId: number
  fieldName?: string
  name: string
  variety: string
  plantDate: string
  growthStage: string
  status: string
}

export interface DiagnosisRecord {
  id: number
  diseaseName: string
  confidence: number
  advice: string
  guidelineTitle?: string
  guidelineExcerpt?: string
  guidelineSource?: string
  imageUrl: string
  status: 'DONE' | 'UNKNOWN' | 'PENDING_REVIEW' | 'REJECTED'
  fieldName?: string
  cropName?: string
  createTime: string
}

export interface FarmingTask {
  id: number
  title: string
  fieldName: string
  cropName: string
  dueDate: string
  priority: '高' | '中' | '低'
  status: '待办' | '进行中' | '已完成'
}

export interface TrendPoint {
  date: string
  value: number
}

export interface DashboardOverview {
  farmCount: number
  fieldCount: number
  cropCount: number
  diagnosisToday: number
  unknownToday: number
  taskTodo: number
  weatherTrend: TrendPoint[]
  pestTrend: TrendPoint[]
  marketTrend: TrendPoint[]
  recentDiagnoses: DiagnosisRecord[]
}

export interface ModelMonitor {
  accuracy: number
  precision: number
  recall: number
  driftScore: number
  unknownRate: number
  version: string
  accuracyTrend: TrendPoint[]
  unknownSamples: DiagnosisRecord[]
}

export interface PageResult<T> {
  total: number
  records: T[]
}
