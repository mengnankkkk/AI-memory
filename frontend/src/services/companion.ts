import api from './api'
import type { Companion, CompanionCreate, ChatRequest, ChatResponse } from '@/types'

export const companionService = {
  // 创建伙伴
  create(data: CompanionCreate): Promise<Companion> {
    return api.post('/companions/', data)
  },

  // 获取伙伴信息
  get(id: number): Promise<Companion> {
    return api.get(`/companions/${id}`)
  },

  // 更新伙伴信息
  update(id: number, data: Partial<Companion>): Promise<Companion> {
    return api.put(`/companions/${id}`, data)
  },

  // 重置伙伴
  reset(id: number): Promise<{ message: string }> {
    return api.post(`/companions/${id}/reset`)
  },

  // 删除伙伴
  delete(id: number): Promise<{ message: string }> {
    return api.delete(`/companions/${id}`)
  }
}

export const chatService = {
  // 发送消息
  sendMessage(data: ChatRequest): Promise<ChatResponse> {
    return api.post('/chat/', data)
  },

  // 清除会话
  clearSession(sessionId: string): Promise<{ message: string }> {
    return api.delete(`/chat/sessions/${sessionId}`)
  }
}
