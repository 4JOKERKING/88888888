<template>
  <el-row :gutter="16">
    <el-col :span="10">
      <el-card>
        <template #header>农事日历</template>
        <el-calendar v-model="calendarDate">
          <template #date-cell="{ data }">
            <div class="cell">
              <div>{{ data.day.split('-')[2] }}</div>
              <el-tag v-if="taskMap[data.day]" size="small" type="warning">{{ taskMap[data.day] }}项</el-tag>
            </div>
          </template>
        </el-calendar>
      </el-card>
    </el-col>
    <el-col :span="14">
      <el-card>
        <template #header>
          <div class="head">
            <span>待办任务</span>
            <el-button type="primary" @click="openCreate">新建任务</el-button>
          </div>
        </template>
        <el-table :data="tasks" stripe>
          <el-table-column prop="title" label="任务" />
          <el-table-column prop="fieldName" label="地块" width="120" />
          <el-table-column prop="dueDate" label="截止日期" width="120" />
          <el-table-column prop="priority" label="优先级" width="90" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column label="操作" width="140">
            <template #default="{ row }">
              <el-button v-if="row.status !== '已完成'" link type="success" @click="complete(row.id)">完成</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>

    <el-dialog v-model="visible" title="新建农事任务" width="460px">
      <el-form label-width="90px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="地块"><el-input v-model="form.fieldName" /></el-form-item>
        <el-form-item label="作物"><el-input v-model="form.cropName" /></el-form-item>
        <el-form-item label="截止日期"><el-date-picker v-model="form.dueDate" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority" style="width:100%">
            <el-option label="高" value="高" /><el-option label="中" value="中" /><el-option label="低" value="低" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </el-row>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createFarmingTask, getFarmingTasks, updateFarmingTask } from '@/api/farming'
import type { FarmingTask } from '@/types'

const calendarDate = ref(new Date())
const tasks = ref<FarmingTask[]>([])
const visible = ref(false)
const form = reactive<Partial<FarmingTask>>({ title: '', fieldName: '', cropName: '', dueDate: '', priority: '中' })

const taskMap = computed(() => {
  const map: Record<string, number> = {}
  tasks.value.forEach((t) => { map[t.dueDate] = (map[t.dueDate] || 0) + 1 })
  return map
})

async function loadData() {
  const res = await getFarmingTasks()
  tasks.value = res.data.data
}

function openCreate() {
  Object.assign(form, { title: '', fieldName: '', cropName: '', dueDate: '', priority: '中' })
  visible.value = true
}

async function save() {
  if (!form.title || !form.dueDate) return ElMessage.warning('请填写任务标题和截止日期')
  await createFarmingTask(form)
  ElMessage.success('已创建')
  visible.value = false
  await loadData()
}

async function complete(id: number) {
  await updateFarmingTask(id, { status: '已完成' })
  ElMessage.success('已完成')
  await loadData()
}

onMounted(loadData)
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; }
.cell { min-height: 48px; }
</style>
