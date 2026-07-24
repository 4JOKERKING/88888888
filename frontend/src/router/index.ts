import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      redirect: '/dashboard',
      children: [
        { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/DashboardView.vue'), meta: { title: '态势大屏' } },
        { path: 'archive', name: 'Archive', component: () => import('@/views/ArchiveManageView.vue'), meta: { title: '农场档案' } },
        { path: 'diagnosis', name: 'Diagnosis', component: () => import('@/views/DiagnosisView.vue'), meta: { title: '智能诊断' } },
        { path: 'calendar', name: 'Calendar', component: () => import('@/views/FarmingCalendarView.vue'), meta: { title: '农事日历' } },
        { path: 'monitor', name: 'Monitor', component: () => import('@/views/MonitorView.vue'), meta: { title: '模型监控' } }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  if (!to.meta.public && !userStore.isLogin) return '/login'
  if (to.path === '/login' && userStore.isLogin) return '/dashboard'
  return true
})

export default router
