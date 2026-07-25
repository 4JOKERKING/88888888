import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types'
import { login as loginApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref<UserInfo | null>(null)
  const isLogin = computed(() => !!user.value?.token)

  function loadFromStorage() {
    const raw = localStorage.getItem('agri_user')
    if (raw) user.value = JSON.parse(raw)
  }

  async function login(username: string, password: string) {
    const res = await loginApi({ username, password })
    user.value = res.data.data
    localStorage.setItem('agri_user', JSON.stringify(user.value))
  }

  function logout() {
    user.value = null
    localStorage.removeItem('agri_user')
  }

  loadFromStorage()
  return { user, isLogin, login, logout, loadFromStorage }
})
