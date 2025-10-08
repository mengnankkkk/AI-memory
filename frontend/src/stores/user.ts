/**
 * 用户状态管理
 * 支持用户隔离和会话持久化
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Companion } from '@/types'
import api from '@/services/auth'
import { useAuthStore } from './auth'

export interface ChatSession {
  id: number
  user_id: string
  companion_id: number
  session_title: string
  created_at: string
  updated_at: string
  is_active: boolean
  total_messages: number
}

interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export const useUserStore = defineStore('user', () => {
  // 获取认证store
  const authStore = useAuthStore()
  
  // 用户ID（从认证store获取）
  const userId = computed(() => {
    return authStore.user?.id?.toString() || ''
  })

  // 用户的AI伙伴列表
  const companions = ref<Companion[]>([])
  
  // 当前选中的伙伴
  const currentCompanion = ref<Companion | null>(null)
  
  // 聊天会话历史
  const chatSessions = ref<ChatSession[]>([])
  
  // 当前聊天会话
  const currentSession = ref<ChatSession | null>(null)
  
  // 当前聊天消息
  const chatMessages = ref<ChatMessage[]>([])

  // 计算属性
  const hasCompanions = computed(() => companions.value.length > 0)
  const hasChatHistory = computed(() => chatSessions.value.length > 0)

  // 获取用户的所有AI伙伴
  async function loadUserCompanions() {
    try {
      const response = await api.get('/companions/')
      companions.value = response.data
    } catch (error) {
      console.error('加载AI伙伴失败:', error)
    }
  }

  // 获取聊天会话历史
  async function loadChatSessions(companionId?: number) {
    try {
      let url = `/sessions/${userId.value}/history`
      if (companionId) {
        url += `?companion_id=${companionId}`
      }

      const response = await api.get(url)
      chatSessions.value = response.data
    } catch (error) {
      console.error('加载聊天历史失败:', error)
    }
  }

  // 创建新的聊天会话
  async function createChatSession(companionId: number, title?: string): Promise<ChatSession | null> {
    try {
      const response = await api.post('/sessions/', {
        companion_id: companionId,
        user_id: userId.value,
        session_title: title
      })

      const session = response.data
      currentSession.value = session
      chatSessions.value.unshift(session)
      return session
    } catch (error) {
      console.error('创建聊天会话失败:', error)
    }
    return null
  }

  // 加载聊天消息
  async function loadChatMessages(sessionId: number) {
    try {
      const response = await api.get(`/sessions/${sessionId}/messages?user_id=${userId.value}`)
      chatMessages.value = response.data.messages || []
    } catch (error) {
      console.error('加载聊天消息失败:', error)
    }
  }

  // 设置当前伙伴
  function setCurrentCompanion(companion: Companion) {
    currentCompanion.value = companion
  }

  // 设置当前会话
  function setCurrentSession(session: ChatSession) {
    currentSession.value = session
  }

  // 添加聊天消息
  function addChatMessage(message: ChatMessage) {
    chatMessages.value.push(message)
  }

  // 清空聊天消息
  function clearChatMessages() {
    chatMessages.value = []
  }

  // 重置用户ID（开发时使用）
  function resetUserId() {
    const newUserId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    userId.value = newUserId
    localStorage.setItem('ai_companion_user_id', newUserId)
    
    // 清空所有数据
    companions.value = []
    currentCompanion.value = null
    chatSessions.value = []
    currentSession.value = null
    chatMessages.value = []
  }

  return {
    // 状态
    userId: computed(() => userId.value),
    companions: computed(() => companions.value),
    currentCompanion: computed(() => currentCompanion.value),
    chatSessions,
    currentSession: computed(() => currentSession.value),
    chatMessages: computed(() => chatMessages.value),
    
    // 计算属性
    hasCompanions,
    hasChatHistory,
    
    // 方法
    loadUserCompanions,
    loadChatSessions,
    createChatSession,
    loadChatMessages,
    setCurrentCompanion,
    setCurrentSession,
    addChatMessage,
    clearChatMessages,
    resetUserId
  }
})
