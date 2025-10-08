import api from './auth'
import type { Companion, CompanionCreate, ChatRequest, ChatResponse } from '@/types'

export const companionService = {
  // 创建伙伴
  async create(data: CompanionCreate): Promise<Companion> {
    const response = await api.post('/companions/', data)
    return response
  },

  // 获取伙伴信息
  async get(id: number): Promise<Companion> {
    const response = await api.get(`/companions/${id}`)
    return response.data || response
  },

  // 更新伙伴信息
  async update(id: number, data: Partial<Companion>): Promise<Companion> {
    const response = await api.put(`/companions/${id}`, data)
    return response
  },

  // 重置伙伴
  async reset(id: number): Promise<{ message: string }> {
    const response = await api.post(`/companions/${id}/reset`)
    return response
  },

  // 删除伙伴
  async delete(id: number): Promise<{ message: string }> {
    const response = await api.delete(`/companions/${id}`)
    return response
  }
}

export const chatService = {
  // 发送消息
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    const response = await api.post('/chat/', data)
    return response
  },

  // 清除会话
  async clearSession(sessionId: string): Promise<{ message: string }> {
    const response = await api.delete(`/chat/sessions/${sessionId}`)
    return response
  }
}
