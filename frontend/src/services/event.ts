/**
 * 事件系统API服务
 */
import api from './auth'

export interface EventDialogue {
  speaker: string
  text: string
}

export interface EventScriptContent {
  title: string
  description: string
  image?: string
  dialogue: EventDialogue[]
}

export interface EventData {
  event_id: number
  event_code: string
  event_name: string
  event_type: string
  category: string
  script_content: EventScriptContent
  image_url?: string
  history_id: number
  triggered_at: string
  is_completed: boolean
  companion_name?: string
}

export interface EventHistoryData {
  id: number
  event_code: string
  event_name: string
  triggered_at: string
  completed_at?: string
  is_completed: boolean
  choice_made?: string
}

/**
 * 获取待处理的事件
 */
export async function getPendingEvents(companionId: number): Promise<EventData[]> {
  try {
    const response = await api.get(`/events/pending?companion_id=${companionId}`)
    return response.data
  } catch (error) {
    console.error('获取待处理事件失败:', error)
    return []
  }
}

/**
 * 获取事件历史记录
 */
export async function getEventHistory(
  companionId: number,
  limit: number = 20
): Promise<EventHistoryData[]> {
  try {
    const response = await api.get(`/events/history?companion_id=${companionId}&limit=${limit}`)
    return response.data
  } catch (error) {
    console.error('获取事件历史失败:', error)
    return []
  }
}

/**
 * 完成事件
 */
export async function completeEvent(
  historyId: number,
  choice?: string,
  choiceContent?: string
): Promise<boolean> {
  try {
    await api.post(`/events/${historyId}/complete`, {
      choice,
      choice_content: choiceContent
    })
    return true
  } catch (error) {
    console.error('完成事件失败:', error)
    return false
  }
}

/**
 * 触发事件相关对话
 */
export async function triggerEventConversation(historyId: number): Promise<{
  success: boolean
  event_context?: {
    event_name: string
    event_description: string
    dialogue: EventDialogue[]
  }
}> {
  try {
    const response = await api.post(`/events/${historyId}/trigger-conversation`)
    return response.data
  } catch (error) {
    console.error('触发事件对话失败:', error)
    return { success: false }
  }
}

export const eventApi = {
  getPendingEvents,
  getEventHistory,
  completeEvent,
  triggerEventConversation
}

export default eventApi
