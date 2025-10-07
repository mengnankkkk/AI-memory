import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI, type User } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)

  // 从localStorage恢复状态
  const init = () => {
    const savedToken = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user')

    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }

  // 登录
  const login = async (username: string, password: string) => {
    try {
      const response = await authAPI.login({ username, password })

      token.value = response.access_token
      user.value = response.user

      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '登录失败',
      }
    }
  }

  // 注册
  const register = async (
    username: string,
    email: string,
    password: string
  ) => {
    try {
      const response = await authAPI.register({ username, email, password })

      token.value = response.access_token
      user.value = response.user

      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '注册失败',
      }
    }
  }

  // 登出
  const logout = async () => {
    try {
      await authAPI.logout()
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    }
  }

  // 刷新用户信息
  const refreshUser = async () => {
    try {
      user.value = await authAPI.getCurrentUser()
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (error) {
      // Token无效，清除状态
      logout()
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    init,
    login,
    register,
    logout,
    refreshUser,
  }
})
