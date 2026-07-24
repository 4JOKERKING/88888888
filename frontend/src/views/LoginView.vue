<template>
  <div class="login-page">
    <el-card class="card">
      <h1>云南特色农业智能诊断与生产管理平台</h1>
      <p class="sub">选题三 · 前端模块（何志）</p>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="72px" @keyup.enter="onSubmit">
        <el-form-item label="角色账号" prop="username">
          <el-select v-model="form.username" style="width: 100%">
            <el-option label="农户 farmer" value="farmer" />
            <el-option label="农技人员 tech" value="tech" />
            <el-option label="合作社 coop" value="coop" />
            <el-option label="管理员 admin" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="123456" />
        </el-form-item>
        <el-button type="primary" style="width: 100%" :loading="loading" @click="onSubmit">登录</el-button>
      </el-form>
      <p class="tip">演示密码统一：123456（覆盖农户/农技/合作社/管理员四类角色）</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ username: 'farmer', password: '123456' })
const rules: FormRules = {
  username: [{ required: true, message: '请选择角色账号', trigger: 'change' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background:
    radial-gradient(800px 400px at 20% 10%, rgba(61, 139, 102, 0.25), transparent 60%),
    linear-gradient(160deg, #e8f2ec, #f7f3ea);
}
.card { width: 440px; padding: 12px 8px 4px; }
h1 { font-size: 22px; margin: 0 0 6px; line-height: 1.4; }
.sub { color: #6b7c72; margin-bottom: 18px; }
.tip { margin-top: 14px; text-align: center; color: #8a9790; font-size: 13px; }
</style>
