<template>
  <div class="upload-box">
    <el-upload drag :auto-upload="false" :show-file-list="false" accept="image/*" :on-change="onFileChange">
      <div v-if="!previewUrl" class="placeholder">
        <el-icon :size="42"><UploadFilled /></el-icon>
        <p>拖拽或点击上传作物病害图片</p>
      </div>
      <img v-else :src="previewUrl" class="preview" alt="preview" />
    </el-upload>
    <el-form label-width="80px" class="form">
      <el-form-item label="地块">
        <el-select v-model="fieldId" clearable style="width:100%">
          <el-option v-for="f in fields" :key="f.id" :label="f.name" :value="f.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="作物">
        <el-select v-model="cropId" clearable style="width:100%">
          <el-option v-for="c in crops" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注"><el-input v-model="remark" type="textarea" :rows="2" /></el-form-item>
      <el-button type="primary" :disabled="!file" :loading="loading" @click="submit">开始智能诊断</el-button>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { UploadFile } from 'element-plus'
import { ElMessage } from 'element-plus'
import { uploadDiagnosis } from '@/api/diagnosis'
import { getCrops, getFields } from '@/api/archive'
import type { CropItem, DiagnosisRecord, FieldItem } from '@/types'

const emit = defineEmits<{ success: [DiagnosisRecord] }>()
const file = ref<File | null>(null)
const previewUrl = ref('')
const fieldId = ref<number>()
const cropId = ref<number>()
const remark = ref('')
const loading = ref(false)
const fields = ref<FieldItem[]>([])
const crops = ref<CropItem[]>([])

function onFileChange(uploadFile: UploadFile) {
  const raw = uploadFile.raw
  if (!raw) return
  file.value = raw
  previewUrl.value = URL.createObjectURL(raw)
}

async function submit() {
  if (!file.value) return ElMessage.warning('请先上传图片')
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file.value)
    if (fieldId.value) formData.append('fieldId', String(fieldId.value))
    if (cropId.value) formData.append('cropId', String(cropId.value))
    if (remark.value) formData.append('remark', remark.value)
    const res = await uploadDiagnosis(formData)
    ElMessage.success(res.data.data.status === 'UNKNOWN' ? '已拒识并转入人工审核' : '诊断完成')
    emit('success', res.data.data)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const [f, c] = await Promise.all([getFields(), getCrops()])
  fields.value = f.data.data
  crops.value = c.data.data
})
</script>

<style scoped>
.upload-box { display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px; }
.placeholder { padding: 48px 16px; color: #6b7c72; }
.preview { width: 100%; max-height: 280px; object-fit: contain; }
@media (max-width: 900px) { .upload-box { grid-template-columns: 1fr; } }
</style>
