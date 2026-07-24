import type { AxiosRequestConfig, AxiosResponse } from 'axios'
import type {
  ApiResponse,
  CropItem,
  DashboardOverview,
  DiagnosisRecord,
  FarmItem,
  FarmingTask,
  FieldItem,
  ModelMonitor,
  PageResult,
  UserInfo,
  UserRole
} from '@/types'

const farms: FarmItem[] = [
  { id: 1, name: '普洱绿源家庭农场', ownerName: '李农户', location: '普洱市思茅区', area: 36, status: '运营中' },
  { id: 2, name: '版纳蕉香合作社', ownerName: '王社长', location: '西双版纳景洪市', area: 80, status: '运营中' }
]

const fields: FieldItem[] = [
  { id: 1, farmId: 1, farmName: '普洱绿源家庭农场', name: '一号茶园', area: 12.5, location: '倚象镇A区', status: '种植中' },
  { id: 2, farmId: 1, farmName: '普洱绿源家庭农场', name: '二号茶园', area: 8.0, location: '倚象镇B区', status: '休耕' },
  { id: 3, farmId: 2, farmName: '版纳蕉香合作社', name: '香蕉东区', area: 20, location: '勐罕镇', status: '种植中' }
]

const crops: CropItem[] = [
  { id: 1, fieldId: 1, fieldName: '一号茶园', name: '普洱茶', variety: '大叶种', plantDate: '2025-03-12', growthStage: '成龄期', status: '正常' },
  { id: 2, fieldId: 3, fieldName: '香蕉东区', name: '香蕉', variety: '威廉斯', plantDate: '2025-06-01', growthStage: '结果期', status: '关注' }
]

let diagnoses: DiagnosisRecord[] = [
  {
    id: 1,
    diseaseName: '茶饼病',
    confidence: 0.93,
    advice: '及时摘除病叶，保持通风，必要时喷施保护性杀菌剂。',
    guidelineTitle: '云南茶树主要病害防治技术规范',
    guidelineExcerpt: '茶饼病发病初期应及时摘除病叶并集中销毁，雨季加强排水，药剂防治宜选用保护性杀菌剂。',
    guidelineSource: '《云南省茶树病虫害绿色防控指南》§4.2',
    imageUrl: 'https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=400',
    status: 'DONE',
    fieldName: '一号茶园',
    cropName: '普洱茶',
    createTime: '2026-07-24T09:20:00'
  },
  {
    id: 2,
    diseaseName: '未知样本',
    confidence: 0.41,
    advice: '模型拒识，已进入农技人员人工审核队列。',
    guidelineTitle: '',
    guidelineExcerpt: '',
    guidelineSource: '',
    imageUrl: 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400',
    status: 'UNKNOWN',
    fieldName: '香蕉东区',
    cropName: '香蕉',
    createTime: '2026-07-24T10:05:00'
  }
]

const tasks: FarmingTask[] = [
  { id: 1, title: '一号茶园摘除病叶', fieldName: '一号茶园', cropName: '普洱茶', dueDate: '2026-07-25', priority: '高', status: '待办' },
  { id: 2, title: '香蕉东区排水巡查', fieldName: '香蕉东区', cropName: '香蕉', dueDate: '2026-07-26', priority: '中', status: '进行中' },
  { id: 3, title: '补施有机肥', fieldName: '一号茶园', cropName: '普洱茶', dueDate: '2026-07-28', priority: '低', status: '待办' }
]

function ok<T>(data: T): AxiosResponse<ApiResponse<T>> {
  return {
    data: { code: 200, message: 'success', data },
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {} as never
  }
}

function fail(message: string, code = 400): AxiosResponse<ApiResponse<null>> {
  return {
    data: { code, message, data: null },
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {} as never
  }
}

function match(url = '', method = 'get', pattern: RegExp, m: string) {
  return method.toLowerCase() === m && pattern.test(url)
}

function parseBody(config: AxiosRequestConfig) {
  if (!config.data) return {}
  if (typeof config.data === 'string') {
    try {
      return JSON.parse(config.data)
    } catch {
      return {}
    }
  }
  return config.data
}

function trend(base: number, n = 7) {
  const arr = []
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    arr.push({
      date: `${d.getMonth() + 1}-${String(d.getDate()).padStart(2, '0')}`,
      value: Math.max(0, Math.round(base + Math.sin(i) * 3 + (Math.random() * 2 - 1)))
    })
  }
  return arr
}

export async function useMock(config?: AxiosRequestConfig): Promise<AxiosResponse | null> {
  if (!config) return null
  const url = config.url || ''
  const method = (config.method || 'get').toLowerCase()

  if (match(url, method, /\/api\/auth\/login$/, 'post')) {
    const body = parseBody(config)
    const roleMap: Record<string, UserRole> = {
      farmer: 'FARMER',
      tech: 'TECH',
      coop: 'COOP',
      admin: 'ADMIN'
    }
    const username = String(body.username || '')
    const password = String(body.password || '')
    if (password !== '123456' || !roleMap[username]) {
      return fail('用户名或密码错误（可用 farmer/tech/coop/admin，密码 123456）', 401)
    }
    const names: Record<string, string> = {
      farmer: '农户演示',
      tech: '农技员演示',
      coop: '合作社管理',
      admin: '系统管理员'
    }
    const data: UserInfo = {
      token: `mock-${username}`,
      userId: Object.keys(roleMap).indexOf(username) + 1,
      username,
      nickname: names[username],
      role: roleMap[username]
    }
    return ok(data)
  }

  if (match(url, method, /\/api\/dashboard\/overview$/, 'get')) {
    const data: DashboardOverview = {
      farmCount: farms.length,
      fieldCount: fields.length,
      cropCount: crops.length,
      diagnosisToday: 5,
      unknownToday: diagnoses.filter((d) => d.status === 'UNKNOWN').length,
      taskTodo: tasks.filter((t) => t.status !== '已完成').length,
      weatherTrend: trend(26),
      pestTrend: trend(4),
      marketTrend: trend(18),
      recentDiagnoses: diagnoses.slice(0, 5)
    }
    return ok(data)
  }

  if (match(url, method, /\/api\/farms$/, 'get')) return ok(farms)
  if (match(url, method, /\/api\/farms$/, 'post')) {
    const body = parseBody(config)
    const item: FarmItem = { id: Date.now(), status: '运营中', area: 1, ownerName: '未命名', location: '', name: '', ...body }
    farms.unshift(item)
    return ok(item)
  }
  if (match(url, method, /\/api\/farms\/\d+$/, 'put')) {
    const id = Number(url.split('/').pop())
    const body = parseBody(config)
    const idx = farms.findIndex((f) => f.id === id)
    if (idx >= 0) farms[idx] = { ...farms[idx], ...body }
    return ok(farms[idx])
  }
  if (match(url, method, /\/api\/farms\/\d+$/, 'delete')) {
    const id = Number(url.split('/').pop())
    const idx = farms.findIndex((f) => f.id === id)
    if (idx >= 0) farms.splice(idx, 1)
    return ok(true)
  }

  if (match(url, method, /\/api\/fields$/, 'get')) return ok(fields)
  if (match(url, method, /\/api\/fields$/, 'post')) {
    const body = parseBody(config)
    const farm = farms.find((f) => f.id === body.farmId)
    const item: FieldItem = {
      id: Date.now(),
      farmId: body.farmId,
      farmName: farm?.name,
      name: body.name,
      area: body.area,
      location: body.location,
      status: body.status || '种植中'
    }
    fields.unshift(item)
    return ok(item)
  }
  if (match(url, method, /\/api\/fields\/\d+$/, 'put')) {
    const id = Number(url.split('/').pop())
    const body = parseBody(config)
    const idx = fields.findIndex((f) => f.id === id)
    if (idx >= 0) {
      const farm = farms.find((f) => f.id === (body.farmId ?? fields[idx].farmId))
      fields[idx] = { ...fields[idx], ...body, farmName: farm?.name }
    }
    return ok(fields[idx])
  }
  if (match(url, method, /\/api\/fields\/\d+$/, 'delete')) {
    const id = Number(url.split('/').pop())
    const idx = fields.findIndex((f) => f.id === id)
    if (idx >= 0) fields.splice(idx, 1)
    return ok(true)
  }

  if (match(url, method, /\/api\/crops$/, 'get')) return ok(crops)
  if (match(url, method, /\/api\/crops$/, 'post')) {
    const body = parseBody(config)
    const field = fields.find((f) => f.id === body.fieldId)
    const item: CropItem = {
      id: Date.now(),
      fieldId: body.fieldId,
      fieldName: field?.name,
      name: body.name,
      variety: body.variety,
      plantDate: body.plantDate,
      growthStage: body.growthStage || '生长期',
      status: body.status || '正常'
    }
    crops.unshift(item)
    return ok(item)
  }
  if (match(url, method, /\/api\/crops\/\d+$/, 'put')) {
    const id = Number(url.split('/').pop())
    const body = parseBody(config)
    const idx = crops.findIndex((c) => c.id === id)
    if (idx >= 0) {
      const field = fields.find((f) => f.id === (body.fieldId ?? crops[idx].fieldId))
      crops[idx] = { ...crops[idx], ...body, fieldName: field?.name }
    }
    return ok(crops[idx])
  }
  if (match(url, method, /\/api\/crops\/\d+$/, 'delete')) {
    const id = Number(url.split('/').pop())
    const idx = crops.findIndex((c) => c.id === id)
    if (idx >= 0) crops.splice(idx, 1)
    return ok(true)
  }

  if (match(url, method, /\/api\/diagnosis\/upload$/, 'post')) {
    await new Promise((r) => setTimeout(r, 700))
    const unknown = Math.random() < 0.25
    const record: DiagnosisRecord = unknown
      ? {
          id: Date.now(),
          diseaseName: '未知样本',
          confidence: 0.38,
          advice: '置信度低于阈值，系统拒识并转入人工审核。',
          guidelineTitle: '',
          guidelineExcerpt: '',
          guidelineSource: '',
          imageUrl: 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400',
          status: 'UNKNOWN',
          fieldName: '一号茶园',
          cropName: '普洱茶',
          createTime: new Date().toISOString()
        }
      : {
          id: Date.now(),
          diseaseName: '茶炭疽病',
          confidence: 0.9,
          advice: '清除病残叶，雨后补喷保护性药剂，避免偏施氮肥。',
          guidelineTitle: '茶树炭疽病绿色防控要点',
          guidelineExcerpt: '发病初期摘除病叶，合理修剪增强通透性；药剂防治应轮换用药，严格执行安全间隔期。',
          guidelineSource: '《茶树病虫害综合防治手册》§3.1',
          imageUrl: 'https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=400',
          status: 'DONE',
          fieldName: '一号茶园',
          cropName: '普洱茶',
          createTime: new Date().toISOString()
        }
    diagnoses = [record, ...diagnoses]
    if (!unknown) {
      tasks.unshift({
        id: Date.now() + 1,
        title: `处置：${record.diseaseName}`,
        fieldName: record.fieldName || '',
        cropName: record.cropName || '',
        dueDate: new Date(Date.now() + 86400000).toISOString().slice(0, 10),
        priority: '高',
        status: '待办'
      })
    }
    return ok(record)
  }

  if (match(url, method, /\/api\/diagnosis\/\d+\/review$/, 'post')) {
    const id = Number(url.split('/')[3])
    const body = parseBody(config)
    const idx = diagnoses.findIndex((d) => d.id === id)
    if (idx >= 0) {
      diagnoses[idx] = {
        ...diagnoses[idx],
        status: body.action === 'APPROVE' ? 'DONE' : 'REJECTED',
        diseaseName: body.action === 'APPROVE' ? (body.diseaseName || '人工确认病害') : diagnoses[idx].diseaseName,
        advice: body.comment || diagnoses[idx].advice
      }
      return ok(diagnoses[idx])
    }
    return fail('记录不存在', 404)
  }

  if (match(url, method, /\/api\/diagnosis$/, 'get')) {
    const params = config.params || {}
    let list = [...diagnoses]
    if (params.keyword) {
      const kw = String(params.keyword)
      list = list.filter((d) => d.diseaseName.includes(kw) || (d.cropName || '').includes(kw))
    }
    if (params.status) list = list.filter((d) => d.status === params.status)
    const page = Number(params.page || 1)
    const pageSize = Number(params.pageSize || 10)
    const start = (page - 1) * pageSize
    const data: PageResult<DiagnosisRecord> = { total: list.length, records: list.slice(start, start + pageSize) }
    return ok(data)
  }

  if (match(url, method, /\/api\/farming-tasks$/, 'get')) return ok(tasks)
  if (match(url, method, /\/api\/farming-tasks$/, 'post')) {
    const body = parseBody(config)
    const item: FarmingTask = {
      id: Date.now(),
      title: body.title,
      fieldName: body.fieldName || '',
      cropName: body.cropName || '',
      dueDate: body.dueDate,
      priority: body.priority || '中',
      status: '待办'
    }
    tasks.unshift(item)
    return ok(item)
  }
  if (match(url, method, /\/api\/farming-tasks\/\d+$/, 'put')) {
    const id = Number(url.split('/').pop())
    const body = parseBody(config)
    const idx = tasks.findIndex((t) => t.id === id)
    if (idx >= 0) tasks[idx] = { ...tasks[idx], ...body }
    return ok(tasks[idx])
  }

  if (match(url, method, /\/api\/monitor\/model$/, 'get')) {
    const data: ModelMonitor = {
      accuracy: 0.912,
      precision: 0.894,
      recall: 0.887,
      driftScore: 0.18,
      unknownRate: 0.07,
      version: 'agri-disease-v1.3.2',
      accuracyTrend: trend(90).map((x) => ({ ...x, value: 88 + (x.value % 5) })),
      unknownSamples: diagnoses.filter((d) => d.status === 'UNKNOWN' || d.status === 'PENDING_REVIEW')
    }
    return ok(data)
  }

  return null
}
