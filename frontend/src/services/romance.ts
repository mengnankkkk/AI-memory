/**
 * 恋爱攻略系统 API 服务
 */
import api from './auth'
import type {
  CompanionStateResponse,
  GiftRequest,
  GiftResponse,
  RandomEventResponse,
  InteractionAnalysisRequest,
  InteractionAnalysisResponse,
  DailyTaskResponse,
  StoreItemResponse,
  UserCurrencyResponse,
  CompanionChatContextRequest,
  CompanionChatContextResponse
} from '@/types/romance'

const API_BASE = '/romance'

class RomanceApi {
  /**
   * 获取伙伴状态
   */
  async getCompanionState(companionId: number, userId: string): Promise<CompanionStateResponse> {
    const response = await api.get(`${API_BASE}/companion/${companionId}/state?user_id=${userId}`)
    return response
  }

  /**
   * 赠送礼物
   */
  async giveGift(companionId: number, giftRequest: GiftRequest): Promise<GiftResponse> {
    const response = await api.post(`${API_BASE}/companion/${companionId}/gift`, giftRequest)
    return response
  }

  /**
   * 触发随机事件
   */
  async triggerRandomEvent(companionId: number, userId: string): Promise<RandomEventResponse> {
    const response = await api.post(`${API_BASE}/companion/${companionId}/random-event?user_id=${userId}`)
    return response
  }

  /**
   * 获取待处理事件
   */
  async getPendingEvents(companionId: number, userId: string): Promise<{ events: any[] }> {
    const response = await api.get(`${API_BASE}/companion/${companionId}/pending-events?user_id=${userId}`)
    return response
  }

  /**
   * 分析交互
   */
  async analyzeInteraction(request: InteractionAnalysisRequest): Promise<InteractionAnalysisResponse> {
    const response = await api.post(`${API_BASE}/companion/${request.companion_id}/analyze-interaction`, request)
    return response
  }

  /**
   * 获取每日任务
   */
  async getDailyTasks(companionId: number, userId: string): Promise<DailyTaskResponse[]> {
    const response = await api.get(`${API_BASE}/companion/${companionId}/daily-tasks?user_id=${userId}`)
    return response
  }

  /**
   * 完成每日任务
   */
  async completeTask(taskId: string, companionId: number, userId: string): Promise<{ success: boolean; reward: number }> {
    const response = await api.post(`${API_BASE}/companion/${companionId}/tasks/${taskId}/complete`, { user_id: userId })
    return response
  }

  /**
   * 获取商店物品
   */
  async getStoreItems(itemType?: string, rarity?: string): Promise<StoreItemResponse[]> {
    const params = new URLSearchParams()
    if (itemType) params.append('item_type', itemType)
    if (rarity) params.append('rarity', rarity)
    
    const url = `${API_BASE}/store/items${params.toString() ? '?' + params.toString() : ''}`
    const response = await api.get(url)
    
    // 为礼物添加表情符号
    return response.map((item: StoreItemResponse) => ({
      ...item,
      emoji: this.getGiftEmoji(item.item_type)
    }))
  }

  /**
   * 购买物品
   */
  async purchaseItem(itemId: string, userId: string): Promise<{ success: boolean; message: string }> {
    const response = await api.post(`${API_BASE}/store/purchase`, { item_id: itemId, user_id: userId })
    return response
  }

  /**
   * 获取用户货币
   */
  async getUserCurrency(userId: string): Promise<UserCurrencyResponse> {
    const response = await api.get(`${API_BASE}/user/${userId}/currency`)
    return response
  }

  /**
   * 获取聊天上下文（包含恋爱状态）
   */
  async getChatContext(request: CompanionChatContextRequest): Promise<CompanionChatContextResponse> {
    const response = await api.post(`${API_BASE}/companion/${request.companion_id}/chat-context`, request)
    return response
  }

  /**
   * 获取关系统计
   */
  async getRelationshipStats(userId: string): Promise<{
    total_companions: number
    highest_affinity: number
    total_gifts_given: number
    total_interactions: number
    average_affinity: number
  }> {
    const response = await api.get(`${API_BASE}/user/${userId}/relationship-stats`)
    return response
  }

  /**
   * 获取成就列表
   */
  async getAchievements(userId: string): Promise<{
    id: string
    name: string
    description: string
    unlocked: boolean
    progress: number
    max_progress: number
    reward: string
  }[]> {
    const response = await api.get(`${API_BASE}/user/${userId}/achievements`)
    return response
  }

  /**
   * 导出关系数据
   */
  async exportRelationshipData(userId: string, companionId: number): Promise<Blob> {
    const response = await api.get(`${API_BASE}/companion/${companionId}/export?user_id=${userId}`, {
      responseType: 'blob'
    })
    return response
  }

  /**
   * 重置关系状态（开发用）
   */
  async resetRelationship(companionId: number, userId: string): Promise<{ success: boolean }> {
    const response = await api.post(`${API_BASE}/companion/${companionId}/reset`, { user_id: userId })
    return response
  }

  /**
   * 获取礼物对应的表情符号
   */
  private getGiftEmoji(itemType: string): string {
    const emojiMap: Record<string, string> = {
      'flower': '🌹',
      'chocolate': '🍫',
      'jewelry': '💎',
      'book': '📚',
      'game': '🎮',
      'outfit': '👗',
      'teddy': '🧸',
      'music': '🎵',
      'food': '🍰',
      'perfume': '🌸',
      'watch': '⌚',
      'necklace': '📿'
    }
    return emojiMap[itemType] || '🎁'
  }

  /**
   * 获取推荐礼物
   */
  async getRecommendedGifts(companionId: number, userId: string): Promise<StoreItemResponse[]> {
    const response = await api.get(`${API_BASE}/companion/${companionId}/recommended-gifts?user_id=${userId}`)
    
    return response.map((item: StoreItemResponse) => ({
      ...item,
      emoji: this.getGiftEmoji(item.item_type)
    }))
  }

  /**
   * 获取关系历史
   */
  async getRelationshipHistory(companionId: number, userId: string, days: number = 30): Promise<{
    date: string
    affinity_score: number
    interactions: number
    events: string[]
  }[]> {
    const response = await api.get(`${API_BASE}/companion/${companionId}/history?user_id=${userId}&days=${days}`)
    return response
  }
}

// 创建单例实例
export const romanceApi = new RomanceApi()
export default romanceApi
