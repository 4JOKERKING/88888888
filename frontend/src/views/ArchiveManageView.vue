<template>
  <el-card>
    <el-tabs v-model="tab">
      <el-tab-pane label="农场管理" name="farms">
        <div class="toolbar"><el-button type="primary" @click="openFarm()">新增农场</el-button></div>
        <el-table :data="farms" stripe>
          <el-table-column prop="name" label="农场名称" />
          <el-table-column prop="ownerName" label="负责人" />
          <el-table-column prop="location" label="位置" />
          <el-table-column prop="area" label="面积(亩)" width="110" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button link type="primary" @click="openFarm(row)">编辑</el-button>
              <el-button link type="danger" @click="removeFarm(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="地块管理" name="fields">
        <div class="toolbar"><el-button type="primary" @click="openField()">新增地块</el-button></div>
        <el-table :data="fields" stripe>
          <el-table-column prop="name" label="地块" />
          <el-table-column prop="farmName" label="所属农场" />
          <el-table-column prop="area" label="面积(亩)" width="110" />
          <el-table-column prop="location" label="位置" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button link type="primary" @click="openField(row)">编辑</el-button>
              <el-button link type="danger" @click="removeField(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="种植档案" name="crops">
        <div class="toolbar"><el-button type="primary" @click="openCrop()">新增作物档案</el-button></div>
        <el-table :data="crops" stripe>
          <el-table-column prop="name" label="作物" />
          <el-table-column prop="variety" label="品种" />
          <el-table-column prop="fieldName" label="地块" />
          <el-table-column prop="plantDate" label="种植日期" width="120" />
          <el-table-column prop="growthStage" label="生育期" width="100" />
          <el-table-column prop="status" label="状态" width="90" />
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button link type="primary" @click="openCrop(row)">编辑</el-button>
              <el-button link type="danger" @click="removeCrop(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="farmVisible" :title="farmForm.id ? '编辑农场' : '新增农场'" width="480px">
      <el-form label-width="90px">
        <el-form-item label="名称"><el-input v-model="farmForm.name" /></el-form-item>
        <el-form-item label="负责人"><el-input v-model="farmForm.ownerName" /></el-form-item>
        <el-form-item label="位置"><el-input v-model="farmForm.location" /></el-form-item>
        <el-form-item label="面积"><el-input-number v-model="farmForm.area" :min="0" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="farmVisible=false">取消</el-button><el-button type="primary" @click="saveFarm">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="fieldVisible" :title="fieldForm.id ? '编辑地块' : '新增地块'" width="480px">
      <el-form label-width="90px">
        <el-form-item label="名称"><el-input v-model="fieldForm.name" /></el-form-item>
        <el-form-item label="农场">
          <el-select v-model="fieldForm.farmId" style="width:100%"><el-option v-for="f in farms" :key="f.id" :label="f.name" :value="f.id" /></el-select>
        </el-form-item>
        <el-form-item label="位置"><el-input v-model="fieldForm.location" /></el-form-item>
        <el-form-item label="面积"><el-input-number v-model="fieldForm.area" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="fieldForm.status" style="width:100%"><el-option label="种植中" value="种植中" /><el-option label="休耕" value="休耕" /></el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="fieldVisible=false">取消</el-button><el-button type="primary" @click="saveField">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="cropVisible" :title="cropForm.id ? '编辑作物档案' : '新增作物档案'" width="480px">
      <el-form label-width="90px">
        <el-form-item label="作物"><el-input v-model="cropForm.name" /></el-form-item>
        <el-form-item label="品种"><el-input v-model="cropForm.variety" /></el-form-item>
        <el-form-item label="地块">
          <el-select v-model="cropForm.fieldId" style="width:100%"><el-option v-for="f in fields" :key="f.id" :label="f.name" :value="f.id" /></el-select>
        </el-form-item>
        <el-form-item label="种植日期"><el-date-picker v-model="cropForm.plantDate" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="生育期"><el-input v-model="cropForm.growthStage" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="cropVisible=false">取消</el-button><el-button type="primary" @click="saveCrop">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createCrop, createFarm, createField, deleteCrop, deleteFarm, deleteField,
  getCrops, getFarms, getFields, updateCrop, updateFarm, updateField
} from '@/api/archive'
import type { CropItem, FarmItem, FieldItem } from '@/types'

const tab = ref('farms')
const farms = ref<FarmItem[]>([])
const fields = ref<FieldItem[]>([])
const crops = ref<CropItem[]>([])

const farmVisible = ref(false)
const fieldVisible = ref(false)
const cropVisible = ref(false)
const farmForm = reactive<Partial<FarmItem>>({})
const fieldForm = reactive<Partial<FieldItem>>({})
const cropForm = reactive<Partial<CropItem>>({})

async function loadAll() {
  const [a, b, c] = await Promise.all([getFarms(), getFields(), getCrops()])
  farms.value = a.data.data
  fields.value = b.data.data
  crops.value = c.data.data
}

function openFarm(row?: FarmItem) {
  Object.assign(farmForm, row || { id: undefined, name: '', ownerName: '', location: '', area: 1, status: '运营中' })
  farmVisible.value = true
}
async function saveFarm() {
  if (!farmForm.name) return ElMessage.warning('请填写农场名称')
  if (farmForm.id) await updateFarm(farmForm.id, farmForm)
  else await createFarm(farmForm)
  ElMessage.success('已保存')
  farmVisible.value = false
  await loadAll()
}
async function removeFarm(id: number) {
  await ElMessageBox.confirm('确认删除农场？', '提示', { type: 'warning' })
  await deleteFarm(id)
  await loadAll()
}

function openField(row?: FieldItem) {
  Object.assign(fieldForm, row || { id: undefined, name: '', farmId: farms.value[0]?.id, location: '', area: 1, status: '种植中' })
  fieldVisible.value = true
}
async function saveField() {
  if (!fieldForm.name || !fieldForm.farmId) return ElMessage.warning('请完善地块信息')
  if (fieldForm.id) await updateField(fieldForm.id, fieldForm)
  else await createField(fieldForm)
  ElMessage.success('已保存')
  fieldVisible.value = false
  await loadAll()
}
async function removeField(id: number) {
  await ElMessageBox.confirm('确认删除地块？', '提示', { type: 'warning' })
  await deleteField(id)
  await loadAll()
}

function openCrop(row?: CropItem) {
  Object.assign(cropForm, row || { id: undefined, name: '', variety: '', fieldId: fields.value[0]?.id, plantDate: '', growthStage: '生长期', status: '正常' })
  cropVisible.value = true
}
async function saveCrop() {
  if (!cropForm.name || !cropForm.fieldId) return ElMessage.warning('请完善作物档案')
  if (cropForm.id) await updateCrop(cropForm.id, cropForm)
  else await createCrop(cropForm)
  ElMessage.success('已保存')
  cropVisible.value = false
  await loadAll()
}
async function removeCrop(id: number) {
  await ElMessageBox.confirm('确认删除作物档案？', '提示', { type: 'warning' })
  await deleteCrop(id)
  await loadAll()
}

onMounted(loadAll)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
</style>
