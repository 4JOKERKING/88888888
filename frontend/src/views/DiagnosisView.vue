<template>
  <div>
    <el-card>
      <template #header>病害图片上传与识别</template>
      <DiagnosisUpload @success="onSuccess" />
    </el-card>

    <el-card v-if="result" style="margin-top: 16px">
      <template #header>识别结果可视化</template>
      <el-row :gutter="16">
        <el-col :span="8">
          <el-image :src="result.imageUrl" fit="cover" style="width:100%;height:240px;border-radius:8px" />
          <el-progress :percentage="Math.round(result.confidence * 100)" :status="result.status === 'UNKNOWN' ? 'exception' : 'success'" style="margin-top:12px" />
        </el-col>
        <el-col :span="16">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="识别结果">{{ result.diseaseName }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="statusType(result.status)">{{ statusText(result.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="地块/作物">{{ result.fieldName || '-' }} / {{ result.cropName || '-' }}</el-descriptions-item>
            <el-descriptions-item label="防治建议">{{ result.advice }}</el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="result && result.guidelineExcerpt" style="margin-top: 16px">
      <template #header>防治建议及规范原文对照</template>
      <el-row :gutter="16">
        <el-col :span="12">
          <h4>系统建议</h4>
          <p>{{ result.advice }}</p>
        </el-col>
        <el-col :span="12">
          <h4>{{ result.guidelineTitle }}</h4>
          <p class="excerpt">{{ result.guidelineExcerpt }}</p>
          <el-text type="info">来源：{{ result.guidelineSource }}</el-text>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top: 16px">
      <template #header>
        <div class="head">
          <span>诊断记录</span>
          <div>
            <el-input v-model="keyword" placeholder="搜索" clearable style="width:180px;margin-right:8px" />
            <el-select v-model="status" clearable placeholder="状态" style="width:140px;margin-right:8px">
              <el-option label="已完成" value="DONE" />
              <el-option label="未知拒识" value="UNKNOWN" />
              <el-option label="已驳回" value="REJECTED" />
            </el-select>
            <el-button type="primary" @click="loadList">查询</el-button>
          </div>
        </div>
      </template>
      <el-table :data="records" stripe>
        <el-table-column prop="diseaseName" label="结果" />
        <el-table-column prop="cropName" label="作物" />
        <el-table-column label="置信度" width="100"><template #default="{ row }">{{ (row.confidence * 100).toFixed(1) }}%</template></el-table-column>
        <el-table-column label="状态" width="110"><template #default="{ row }"><el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag></template></el-table-column>
        <el-table-column prop="createTime" label="时间" width="180" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button link type="primary" @click="result = row">查看</el-button>
            <el-button v-if="canReview && row.status === 'UNKNOWN'" link type="warning" @click="review(row.id, 'APPROVE')">通过</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import DiagnosisUpload from '@/components/DiagnosisUpload.vue'
import { getDiagnosisList, reviewDiagnosis } from '@/api/diagnosis'
import { useUserStore } from '@/stores/user'
import type { DiagnosisRecord } from '@/types'

const userStore = useUserStore()
const result = ref<DiagnosisRecord | null>(null)
const records = ref<DiagnosisRecord[]>([])
const keyword = ref('')
const status = ref('')
const canReview = computed(() => ['TECH', 'ADMIN'].includes(userStore.user?.role || ''))

function statusText(s: string) {
  return ({ DONE: '已完成', UNKNOWN: '未知拒识', PENDING_REVIEW: '待审核', REJECTED: '已驳回' } as Record<string, string>)[s] || s
}
function statusType(s: string) {
  return ({ DONE: 'success', UNKNOWN: 'warning', PENDING_REVIEW: 'info', REJECTED: 'danger' } as Record<string, string>)[s] || 'info'
}

function onSuccess(record: DiagnosisRecord) {
  result.value = record
  loadList()
}

async function loadList() {
  const res = await getDiagnosisList({ page: 1, pageSize: 20, keyword: keyword.value, status: status.value || undefined })
  records.value = res.data.data.records
}

async function review(id: number, action: 'APPROVE' | 'REJECT') {
  await reviewDiagnosis(id, { action, diseaseName: '人工确认病害', comment: '农技人员审核通过' })
  ElMessage.success('审核完成')
  await loadList()
}

onMounted(loadList)
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; }
h4 { margin: 0 0 8px; color: #1f4d3a; }
.excerpt { line-height: 1.7; background: #f5faf7; padding: 12px; border-radius: 8px; }
</style>
