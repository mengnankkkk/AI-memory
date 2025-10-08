/**
 * 系统配置和统计API服务
 */
import apiClient from './auth'

export interface ConfigItem {
  key: string
  value: any
  ttl?: number
}

export interface StatsOverview {
  today: Record<string, number>
  trends: Record<string, Record<string, number>>
}

export interface PerformanceStats {
  cache_hit_rate: number
  success_rate: number
  total_requests: number
  cache_hits: number
  successful_responses: number
  error_responses: number
}

export interface MetricHistory {
  metric: string
  days: number
  data: Record<string, number>
}

export interface ABTestConfig {
  test_name: string
  enabled: boolean
  traffic_split: number
  version_a: string
  version_b: string
}

export const configService = {
  // 配置管理
  async getAllConfigs() {
    const response = await apiClient.get('/config/all')
    return response.configs
  },

  async getConfig(key: string) {
    const response = await apiClient.get(`/config/${key}`)
    return response
  },

  async setConfig(key: string, value: any, ttl?: number) {
    const response = await apiClient.post(`/config/${key}`, { value, ttl })
    return response
  },

  async deleteConfig(key: string) {
    const response = await apiClient.delete(`/config/${key}`)
    return response
  },

  // 统计数据
  async getStatsOverview(): Promise<StatsOverview> {
    const response = await apiClient.get('/stats/overview')
    return response
  },

  async getMetricHistory(metric: string, days: number = 7): Promise<MetricHistory> {
    const response = await apiClient.get(`/stats/metrics/${metric}?days=${days}`)
    return response
  },

  async getPerformanceStats(): Promise<PerformanceStats> {
    const response = await apiClient.get('/stats/performance')
    return response
  },

  async getPromptUsageStats() {
    const response = await apiClient.get('/stats/prompt-usage')
    return response
  },

  async getActiveSessionsStats() {
    const response = await apiClient.get('/stats/active-sessions')
    return response
  },

  // A/B 测试管理
  async getPromptVersions() {
    const response = await apiClient.get('/ab-test/prompt-versions')
    return response
  },

  async switchPromptVersion(companionId: number, version: string) {
    const response = await apiClient.post(`/ab-test/switch-prompt/${companionId}`, { version })
    return response
  },

  async getABTestResults(testName: string, days: number = 7) {
    const response = await apiClient.get(`/ab-test/results/${testName}?days=${days}`)
    return response
  },

  // 通知管理
  async sendNotification(userId: number, type: string, title: string, content: string, data?: any) {
    const response = await apiClient.post('/notification/send', {
      user_id: userId,
      notification_type: type,
      title,
      content,
      data
    })
    return response
  },

  async getUnreadNotifications(userId: number) {
    const response = await apiClient.get(`/notification/unread/${userId}`)
    return response
  },

  // 数据导出
  async exportConversations(params: {
    userId?: number
    companionId?: number
    startDate?: string
    endDate?: string
  }) {
    const queryParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, value.toString())
      }
    })
    
    const response = await apiClient.get(`/export/conversations/csv?${queryParams}`, {
      responseType: 'blob'
    })
    return response
  },

  async exportUserData(userId: number) {
    const response = await apiClient.get(`/export/user-data/${userId}`, {
      responseType: 'blob'
    })
    return response
  }
}
