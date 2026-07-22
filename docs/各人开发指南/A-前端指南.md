# 何志 — 前端开发指南（Vue 3）

> 你的任务：写出全部 6 个页面模块，对接莫成兴的后端 API。

## 你需要做的事

### 页面清单

| 序号 | 页面 | 路由 | 关键组件 |
|------|------|------|---------|
| 1 | 登录/注册 | `/login` `/register` | Element Plus 表单 |
| 2 | 农场与地块管理 | `/farms` `/fields/:id` | 表格 + 弹窗表单 + 树形展开 |
| 3 | 作物档案 | `/crops` | 卡片列表 + 时间线 |
| 4 | **病害诊断**（核心） | `/diagnosis` | 图片上传 + 进度轮询 + 结果卡片 |
| 5 | 农事日历 | `/tasks` | 日历视图 + 任务列表 |
| 6 | 数据看板 | `/dashboard` | ECharts 图表 + 统计卡片 |
| 7 | 模型监控 | `/monitor` | 指标卡片 + 未知样本列表 |

### 项目结构

```
frontend/
├── src/
│   ├── api/              # 所有 API 请求放这里
│   │   ├── index.js      # axios 实例（baseURL, 拦截器）
│   │   ├── auth.js       # 登录/注册
│   │   ├── farm.js       # 农场/地块
│   │   ├── crop.js       # 作物
│   │   ├── diagnosis.js  # 病害诊断
│   │   ├── task.js       # 农事任务
│   │   └── dashboard.js  # 天气/价格/模型
│   ├── views/            # 页面组件
│   ├── components/       # 可复用组件
│   ├── router/           # 路由配置
│   └── stores/           # Pinia 状态管理
```

### 开发顺序（按这个来）

1. **先搭架子**：路由 + 布局框架 + axios 封装 + 登录页
2. **农场/地块管理**：纯 CRUD，最标准，练手
3. **作物档案**：和地块类似
4. **病害诊断**：核心功能，图片上传 + 轮询结果
5. **农事日历**：日历组件 + 任务 CRUD
6. **数据看板**：ECharts 折线图/柱状图
7. **模型监控**：最后做，数据从 API 拿

## 关键代码模式

### 1. axios 封装 (`src/api/index.js`)

```javascript
import axios from 'axios'

const request = axios.create({
  baseURL: 'http://localhost:8080/api',
  timeout: 30000,
})

// 请求拦截器：自动带 token
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default request
```

### 2. API 调用示例 (`src/api/farm.js`)

```javascript
import request from './index'

export const getFarmList = () => request.get('/farms')
export const createFarm = (data) => request.post('/farms', data)
export const getFieldList = (farmId) => request.get('/fields', { params: { farmId } })
export const getFieldDetail = (id) => request.get(`/fields/${id}`)
export const createField = (data) => request.post('/fields', data)
```

### 3. 图片上传组件（病害诊断核心）

```vue
<template>
  <el-upload
    drag
    :action="uploadUrl"
    :headers="{ Authorization: 'Bearer ' + token }"
    :on-success="handleSuccess"
    :on-error="handleError"
    :before-upload="beforeUpload"
    accept="image/jpeg,image/png"
    :limit="1"
  >
    <el-icon><UploadFilled /></el-icon>
    <div>拖拽图片到此处或点击上传</div>
    <template #tip>
      <div>支持 JPG/PNG，不超过 10MB</div>
    </template>
  </el-upload>
</template>

<script setup>
const uploadUrl = 'http://localhost:8080/api/diagnosis/upload'
const token = localStorage.getItem('token')

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片不能超过 10MB')
    return false
  }
  return true
}

const handleSuccess = (response) => {
  // 拿到 diagnosisId，开始轮询结果
  startPolling(response.data.diagnosisId)
}
</script>
```

### 4. 轮询诊断结果

```javascript
const startPolling = (diagnosisId) => {
  const timer = setInterval(async () => {
    const res = await request.get(`/diagnosis/${diagnosisId}`)
    if (res.data.status === 'completed') {
      clearInterval(timer)
      // 展示结果
      showResult(res.data)
    }
  }, 2000) // 每2秒查一次
}
```

### 5. ECharts 图表示例（数据看板）

```vue
<template>
  <div ref="chartRef" style="width:100%;height:300px"></div>
</template>

<script setup>
import * as echarts from 'echarts'
import { ref, onMounted } from 'vue'

const chartRef = ref(null)

onMounted(() => {
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    title: { text: '近期温度趋势' },
    xAxis: { type: 'category', data: ['7/16','7/17','7/18','7/19','7/20','7/21','7/22'] },
    yAxis: { type: 'value', name: '℃' },
    series: [{ data: [26,28,24,22,25,27,24], type: 'line', smooth: true }]
  })
})
</script>
```

## 调试技巧

1. **F12 打开浏览器开发者工具 → Network 面板**
   - 看请求是否发出去了（Status 是 200 还是 400/500）
   - 看请求参数对不对
   - 看返回数据对不对

2. **跨域问题**：如果后端没配 CORS，在 `vite.config.ts` 加：
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
```

3. **Element Plus 组件文档**：https://element-plus.org/zh-CN/component/overview
4. **ECharts 示例**：https://echarts.apache.org/examples/zh/index.html

## 何时找莫成兴（后端）

- 接口返回的数据结构和文档不一致
- 接口 500 错误
- 需要新的接口（字段不够用）
