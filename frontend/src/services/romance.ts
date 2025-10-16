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
    const { data } = await api.get(`${API_BASE}/companion/${companionId}/state?user_id=${userId}`)
    return data
  }

  /**
   * 赠送礼物
   */
  async giveGift(companionId: number, giftRequest: GiftRequest): Promise<GiftResponse> {
    const { data } = await api.post(`${API_BASE}/companion/${companionId}/gift`, giftRequest)
    return data
  }

  /**
   * 触发随机事件
   */
  async triggerRandomEvent(companionId: number, userId: string): Promise<RandomEventResponse> {
    const { data } = await api.post(`${API_BASE}/companion/${companionId}/random-event?user_id=${userId}`)
    return data
  }

  /**
   * 获取待处理事件
   */
  async getPendingEvents(companionId: number, userId: string): Promise<{ events: any[] }> {
    const { data } = await api.get(`${API_BASE}/companion/${companionId}/pending-events?user_id=${userId}`)
    return data
  }

  /**
   * 分析交互
   */
  async analyzeInteraction(request: InteractionAnalysisRequest): Promise<InteractionAnalysisResponse> {
    const { data } = await api.post(`${API_BASE}/companion/${request.companion_id}/analyze-interaction`, request)
    return data
  }

  /**
   * 获取每日任务
   */
  async getDailyTasks(companionId: number, userId: string): Promise<DailyTaskResponse[]> {
    const { data } = await api.get(`${API_BASE}/companion/${companionId}/daily-tasks?user_id=${userId}`)
    return data
  }

  /**
   * 完成每日任务
   */
  async completeTask(taskId: string, companionId: number, userId: string): Promise<{ success: boolean; reward: number }> {
    const { data } = await api.post(`${API_BASE}/companion/${companionId}/tasks/${taskId}/complete`, { user_id: userId })
    return data
  }

  /**
   * 获取商店物品
   */
  async getStoreItems(userId: string, itemType?: string, rarity?: string): Promise<StoreItemResponse[]> {
    const params = new URLSearchParams()
    params.append('user_id', userId)
    if (itemType) params.append('item_type', itemType)
    if (rarity) params.append('rarity', rarity)

    const url = `${API_BASE}/store/items?${params.toString()}`
    const { data } = await api.get(url)

    // preview_url 现在包含 emoji
    return data.map((item: StoreItemResponse) => ({
      ...item,
      emoji: item.preview_url || '🎁'
    }))
  }

  /**
   * 购买物品
   */
  async purchaseItem(itemId: string, userId: string): Promise<{ success: boolean; message: string }> {
    const { data } = await api.post(`${API_BASE}/store/purchase`, { item_id: itemId, user_id: userId })
    return data
  }

  /**
   * 获取用户货币
   */
  async getUserCurrency(userId: string): Promise<UserCurrencyResponse> {
    const { data } = await api.get(`${API_BASE}/user/${userId}/currency`)
    return data
  }

  /**
   * 获取聊天上下文（包含恋爱状态）
   */
  async getChatContext(request: CompanionChatContextRequest): Promise<CompanionChatContextResponse> {
    const { data } = await api.post(`${API_BASE}/companion/${request.companion_id}/chat-context`, request)
    return data
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
    const { data } = await api.get(`${API_BASE}/user/${userId}/relationship-stats`)
    return data
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
    const { data } = await api.get(`${API_BASE}/user/${userId}/achievements`)
    return data
  }

  /**
   * 导出关系数据
   */
  async exportRelationshipData(userId: string, companionId: number): Promise<Blob> {
    const response = await api.get(`${API_BASE}/companion/${companionId}/export?user_id=${userId}`, {
      responseType: 'blob'
    })
    return response.data
  }

  /**
   * 重置关系状态（开发用）
   */
  async resetRelationship(companionId: number, userId: string): Promise<{ success: boolean }> {
    const { data } = await api.post(`${API_BASE}/companion/${companionId}/reset`, { user_id: userId })
    return data
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
    const { data } = await api.get(`${API_BASE}/companion/${companionId}/recommended-gifts?user_id=${userId}`)
    
    return data.map((item: StoreItemResponse) => ({
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
    const { data } = await api.get(`${API_BASE}/companion/${companionId}/history?user_id=${userId}&days=${days}`)
    return data
  }
}

// 创建单例实例
export const romanceApi = new RomanceApi()
export default romanceApi
