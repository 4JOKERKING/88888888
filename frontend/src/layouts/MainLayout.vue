<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="brand">
        <div class="logo">滇</div>
        <div>
          <strong>云南智慧农业</strong>
          <p>智能诊断 · 生产管理</p>
        </div>
      </div>
      <el-menu :default-active="route.path" router background-color="#1f4d3a" text-color="#dcefe4" active-text-color="#ffffff">
        <el-menu-item index="/dashboard"><el-icon><DataAnalysis /></el-icon><span>态势大屏</span></el-menu-item>
        <el-menu-item index="/archive"><el-icon><OfficeBuilding /></el-icon><span>农场档案</span></el-menu-item>
        <el-menu-item index="/diagnosis"><el-icon><Camera /></el-icon><span>智能诊断</span></el-menu-item>
        <el-menu-item index="/calendar"><el-icon><Calendar /></el-icon><span>农事日历</span></el-menu-item>
        <el-menu-item index="/monitor"><el-icon><Monitor /></el-icon><span>模型监控</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="title">{{ route.meta.title || '工作台' }}</div>
        <div class="right">
          <el-tag size="small" type="success">{{ roleLabel }}</el-tag>
          <span>{{ userStore.user?.nickname }}</span>
          <el-button link type="primary" @click="onLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main"><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const roleLabel = computed(() => {
  const map: Record<string, string> = {
    FARMER: '农户',
    TECH: '农技人员',
    COOP: '合作社管理',
    ADMIN: '管理员'
  }
  return map[userStore.user?.role || ''] || '用户'
})

function onLogout() {
  userStore.logout()
  ElMessage.success('已退出')
  router.push('/login')
}
</script>

<style scoped>
.layout { min-height: 100vh; }
.aside { background: #1f4d3a; color: #fff; }
.brand { display: flex; gap: 12px; align-items: center; padding: 18px 16px; border-bottom: 1px solid rgba(255,255,255,.08); }
.brand p { margin: 4px 0 0; font-size: 12px; opacity: .75; }
.logo { width: 40px; height: 40px; border-radius: 10px; display: grid; place-items: center; background: linear-gradient(135deg,#3d8b66,#2f6b4f); font-weight: 700; }
.header { background: #fff; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e6ece8; }
.title { font-size: 18px; font-weight: 600; }
.right { display: flex; align-items: center; gap: 12px; }
.main { padding: 20px; }
.el-menu { border-right: none; }
</style>
