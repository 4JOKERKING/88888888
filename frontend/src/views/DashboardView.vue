<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="4" v-for="item in cards" :key="item.label">
        <el-card shadow="hover"><div class="label">{{ item.label }}</div><div class="value">{{ item.value }}</div></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="8"><el-card><template #header>天气趋势（气温）</template><div ref="weatherRef" class="chart"></div></el-card></el-col>
      <el-col :span="8"><el-card><template #header>病虫害发生趋势</template><div ref="pestRef" class="chart"></div></el-card></el-col>
      <el-col :span="8"><el-card><template #header>市场价格趋势</template><div ref="marketRef" class="chart"></div></el-card></el-col>
    </el-row>

    <el-card style="margin-top: 16px">
      <template #header>最新诊断动态</template>
      <el-table :data="overview?.recentDiagnoses || []" stripe>
        <el-table-column prop="diseaseName" label="识别结果" />
        <el-table-column prop="cropName" label="作物" />
        <el-table-column prop="fieldName" label="地块" />
        <el-table-column label="置信度"><template #default="{ row }">{{ (row.confidence * 100).toFixed(1) }}%</template></el-table-column>
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="createTime" label="时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getDashboardOverview } from '@/api/dashboard'
import type { DashboardOverview } from '@/types'

const overview = ref<DashboardOverview | null>(null)
const weatherRef = ref<HTMLDivElement>()
const pestRef = ref<HTMLDivElement>()
const marketRef = ref<HTMLDivElement>()
const charts: echarts.ECharts[] = []

const cards = computed(() => [
  { label: '农场数', value: overview.value?.farmCount ?? '-' },
  { label: '地块数', value: overview.value?.fieldCount ?? '-' },
  { label: '作物档案', value: overview.value?.cropCount ?? '-' },
  { label: '今日诊断', value: overview.value?.diagnosisToday ?? '-' },
  { label: '未知样本', value: overview.value?.unknownToday ?? '-' },
  { label: '待办农事', value: overview.value?.taskTodo ?? '-' }
])

function lineOption(titleColor: string, data: { date: string; value: number }[]) {
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 16, top: 24, bottom: 28 },
    xAxis: { type: 'category', data: data.map((i) => i.date) },
    yAxis: { type: 'value' },
    series: [{ type: 'line', smooth: true, data: data.map((i) => i.value), itemStyle: { color: titleColor }, areaStyle: { opacity: 0.12 } }]
  }
}

async function loadData() {
  const res = await getDashboardOverview()
  overview.value = res.data.data
  await nextTick()
  ;[
    [weatherRef.value, overview.value.weatherTrend, '#2f6b4f'],
    [pestRef.value, overview.value.pestTrend, '#c45c26'],
    [marketRef.value, overview.value.marketTrend, '#3b82f6']
  ].forEach(([el, data, color]) => {
    if (!el) return
    const chart = echarts.init(el as HTMLDivElement)
    chart.setOption(lineOption(color as string, data as { date: string; value: number }[]))
    charts.push(chart)
  })
}

function onResize() { charts.forEach((c) => c.resize()) }
onMounted(async () => { await loadData(); window.addEventListener('resize', onResize) })
onBeforeUnmount(() => { window.removeEventListener('resize', onResize); charts.forEach((c) => c.dispose()) })
</script>

<style scoped>
.label { color: #6b7c72; margin-bottom: 8px; }
.value { font-size: 26px; font-weight: 700; color: #1f4d3a; }
.chart { height: 260px; }
</style>
