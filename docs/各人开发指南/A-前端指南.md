# 何志 — 前端开发指南（Vue 3）

> ⚠️ **你只调莫成兴的后端（8080端口），不直接调李珈逾的AI服务（8000端口）。**

## 页面清单与路由

| 序号 | 页面 | 路由 | 调用的后端接口 |
|------|------|------|--------------|
| 1 | 登录/注册 | `/login` `/register` | POST `/api/auth/login` `/register` |
| 2 | 农场管理 | `/farms` | GET/POST `/api/farms` |
| 3 | 地块详细 | `/fields/:id` | GET `/api/fields/{id}`, GET `/api/crops?fieldId=` |
| 4 | **病害诊断** | `/diagnosis` | POST `/api/diagnosis/upload` → 轮询 GET `/api/diagnosis/{id}` |
| 5 | 诊断历史 | `/diagnosis/list` | GET `/api/diagnosis/list` |
| 6 | 农事日历 | `/tasks` | GET/POST `/api/tasks`, PUT `/api/tasks/{id}/status` |
| 7 | 数据看板 | `/dashboard` | GET `/api/weather?location=`, GET `/api/market-prices?cropType=` |

## 关键：病害诊断页面

这是核心功能。流程：**上传图片 → 拿到 diagnosisId → 每2秒轮询结果 → 展示**

```vue
<template>
  <div class="diagnosis-page">
    <!-- 步骤1: 上传图片 -->
    <el-card v-if="!diagnosisId">
      <el-form>
        <el-form-item label="选择地块">
          <el-select v-model="form.fieldId" @change="onFieldChange">
            <el-option v-for="f in fields" :key="f.id" :label="f.name" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择作物">
          <el-select v-model="form.cropId">
            <el-option v-for="c in crops" :key="c.id" :label="c.cropType" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="症状描述">
          <el-input v-model="form.description" type="textarea" placeholder="可选，描述异常情况" />
        </el-form-item>
        <el-upload
          drag
          :action="uploadUrl"
          :headers="authHeader"
          :data="uploadData"
          :on-success="onUploadSuccess"
          :before-upload="beforeUpload"
          accept="image/jpeg,image/png"
          :limit="1">
          <el-icon><UploadFilled /></el-icon>
          <div>拖拽图片到此处或点击上传</div>
        </el-upload>
      </el-form>
    </el-card>

    <!-- 步骤2: 等待结果 -->
    <el-card v-if="diagnosisId && loading">
      <el-skeleton :rows="8" animated />
      <el-progress :percentage="pollProgress" />
      <p>AI正在分析图片...</p>
    </el-card>

    <!-- 步骤3: 展示结果 -->
    <el-card v-if="diagnosisId && result">
      <el-result :icon="riskIcon" :title="result.disease">
        <template #subTitle>
          置信度: {{ (result.confidence * 100).toFixed(0) }}% | 严重度: {{ result.severity }}
        </template>
      </el-result>

      <el-descriptions title="诊断详情" border>
        <el-descriptions-item label="风险等级">
          <el-tag :type="riskTagType">{{ riskLabel }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="天气因素">{{ result.agent_opinion.weather_factor }}</el-descriptions-item>
        <el-descriptions-item label="随访建议">{{ result.agent_opinion.follow_up_days }}天后复查</el-descriptions-item>
      </el-descriptions>

      <el-card header="综合评估">
        <p>{{ result.agent_opinion.overall_assessment }}</p>
      </el-card>

      <el-card header="防治建议">
        <el-steps direction="vertical">
          <el-step v-for="(action, i) in result.agent_opinion.recommended_actions"
            :key="i" :title="action" />
        </el-steps>
        <el-divider />
        <p><strong>参考文献：</strong>{{ result.rag_result.source_title }}</p>
        <p>{{ result.rag_result.source_section }}</p>
      </el-card>

      <el-card header="详细防治方案">
        <pre style="white-space: pre-wrap">{{ result.rag_result.detail }}</pre>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import request from '@/api/index'

const diagnosisId = ref(null)
const result = ref(null)
const loading = ref(false)
const pollProgress = ref(0)

const uploadUrl = 'http://localhost:8080/api/diagnosis/upload'
const authHeader = { Authorization: `Bearer ${localStorage.getItem('token')}` }
const uploadData = computed(() => ({
  fieldId: form.fieldId,
  cropId: form.cropId,
  description: form.description,
}))

const riskTagType = computed(() => {
  const map = { low: 'success', medium: 'warning', high: 'danger', critical: 'danger' }
  return map[result.value?.agent_opinion?.risk_level] || 'info'
})

const riskLabel = computed(() => {
  const map = { low: '低风险', medium: '中风险', high: '高风险', critical: '极高风险' }
  return map[result.value?.agent_opinion?.risk_level] || '未知'
})

const onUploadSuccess = (response) => {
  if (response.code === 200) {
    diagnosisId.value = response.data.diagnosisId
    loading.value = true
    startPolling()
  }
}

const startPolling = () => {
  let count = 0
  const timer = setInterval(async () => {
    count++
    pollProgress.value = Math.min(count * 10, 90)
    const res = await request.get(`/diagnosis/${diagnosisId.value}`)
    if (res.data.status === 'completed') {
      clearInterval(timer)
      pollProgress.value = 100
      loading.value = false
      result.value = res.data
    }
    if (count > 30) { // 60秒超时
      clearInterval(timer)
      loading.value = false
      ElMessage.warning('诊断超时，请刷新重试')
    }
  }, 2000)
}
</script>
```

## API 调用封装

```javascript
// src/api/index.js
import axios from 'axios'

const request = axios.create({
  baseURL: 'http://localhost:8080/api',
  timeout: 30000,
})

request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

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

## 数据看板图表（ECharts）

```javascript
// 天气趋势
const weatherOption = {
  xAxis: { type: 'category', data: dates },
  yAxis: [
    { type: 'value', name: '温度(℃)' },
    { type: 'value', name: '湿度(%)' }
  ],
  series: [
    { name: '温度', type: 'line', data: temps },
    { name: '湿度', type: 'line', yAxisIndex: 1, data: humidities }
  ]
}

// 价格趋势
const priceOption = {
  xAxis: { type: 'category', data: dates },
  yAxis: { type: 'value', name: '元/公斤' },
  series: [{ name: '价格', type: 'line', data: prices, smooth: true }]
}
```

## 调试

1. 先确认莫成兴的后端已启动：`curl http://localhost:8080/api/auth/login`
2. F12 → Network → 看请求是否 200
3. 跨域问题 → 找莫成兴加 CORS 配置
4. Element Plus 文档：https://element-plus.org/zh-CN/
5. ECharts 示例：https://echarts.apache.org/examples/zh/
