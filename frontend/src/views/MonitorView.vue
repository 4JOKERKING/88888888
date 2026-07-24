<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="4" v-for="item in cards" :key="item.label">
        <el-card><div class="label">{{ item.label }}</div><div class="value">{{ item.value }}</div></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="14">
        <el-card>
          <template #header>模型准确率趋势 / 数据漂移监控</template>
          <div ref="chartRef" class="chart"></div>
          <el-alert
            style="margin-top:12px"
            :title="`当前漂移分数 ${monitor?.driftScore ?? '-'}（阈值 0.3），未知样本率 ${((monitor?.unknownRate || 0) * 100).toFixed(1)}%`"
            :type="(monitor?.driftScore || 0) > 0.3 ? 'error' : 'success'"
            show-icon
            :closable="false"
          />
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card>
          <template #header>未知样本监控与人工审核队列</template>
          <el-table :data="monitor?.unknownSamples || []" stripe max-height="360">
            <el-table-column prop="diseaseName" label="样本" />
            <el-table-column label="置信度" width="90">
              <template #default="{ row }">{{ (row.confidence * 100).toFixed(1) }}%</template>
            </el-table-column>
            <el-table-column label="操作" width="140">
              <template #default="{ row }">
                <el-button v-if="canReview" link type="primary" @click="approve(row.id)">确认</el-button>
                <el-button v-if="canReview" link type="danger" @click="reject(row.id)">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { getModelMonitor } from '@/api/monitor'
import { reviewDiagnosis } from '@/api/diagnosis'
import { useUserStore } from '@/stores/user'
import type { ModelMonitor } from '@/types'

const userStore = useUserStore()
const monitor = ref<ModelMonitor | null>(null)
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
const canReview = computed(() => ['TECH', 'ADMIN'].includes(userStore.user?.role || ''))

const cards = computed(() => [
  { label: '模型版本', value: monitor.value?.version ?? '-' },
  { label: 'Accuracy', value: monitor.value ? `${(monitor.value.accuracy * 100).toFixed(1)}%` : '-' },
  { label: 'Precision', value: monitor.value ? `${(monitor.value.precision * 100).toFixed(1)}%` : '-' },
  { label: 'Recall', value: monitor.value ? `${(monitor.value.recall * 100).toFixed(1)}%` : '-' },
  { label: '漂移分数', value: monitor.value?.driftScore ?? '-' },
  { label: '未知样本率', value: monitor.value ? `${(monitor.value.unknownRate * 100).toFixed(1)}%` : '-' }
])

async function loadData() {
  const res = await getModelMonitor()
  monitor.value = res.data.data
  await nextTick()
  if (!chartRef.value) return
  chart ??= echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['准确率'] },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: monitor.value.accuracyTrend.map((i) => i.date) },
    yAxis: { type: 'value', min: 80, max: 100 },
    series: [{ name: '准确率', type: 'line', smooth: true, data: monitor.value.accuracyTrend.map((i) => i.value) }]
  })
}

async function approve(id: number) {
  await reviewDiagnosis(id, { action: 'APPROVE', diseaseName: '人工确认病害', comment: '农技审核通过' })
  ElMessage.success('已确认')
  await loadData()
}
async function reject(id: number) {
  await reviewDiagnosis(id, { action: 'REJECT', comment: '样本无效' })
  ElMessage.success('已驳回')
  await loadData()
}

function onResize() { chart?.resize() }
onMounted(async () => { await loadData(); window.addEventListener('resize', onResize) })
onBeforeUnmount(() => { window.removeEventListener('resize', onResize); chart?.dispose() })
</script>

<style scoped>
.label { color: #6b7c72; margin-bottom: 8px; font-size: 13px; }
.value { font-size: 20px; font-weight: 700; color: #1f4d3a; word-break: break-all; }
.chart { height: 320px; }
</style>
