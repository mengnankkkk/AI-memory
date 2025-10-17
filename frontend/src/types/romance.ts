/**
 * 恋爱攻略系统相关类型定义
 */

export interface CompanionStateResponse {
  affinity_score: number
  trust_score: number
  tension_score: number
  romance_level: string
  current_mood: string
  mood_last_updated: number
  last_interaction_at: number
  total_interactions: number
  days_since_first_meet: number
  special_events_triggered: string[]
  gifts_received: GiftRecord[]
  outfit_unlocked: string[]
  memories: Memory[]
}

export interface GiftRecord {
  type: string
  name: string
  given_at: number
}

export interface Memory {
  content: string
  type: string
  timestamp: number
  importance: number
}

export interface GiftRequest {
  gift_type: string
  gift_name: string
  user_id: string
}

export interface GiftResponse {
  success: boolean
  message: string
  affinity_change: number
  new_affinity_score: number
  companion_reaction: string
}

export interface EventResponse {
  type: string
  title: string
  description: string
  affinity_requirement: number
}

export interface RandomEventResponse {
  event: EventResponse | null
  triggered: boolean
}

export interface RelationshipUpgradeResponse {
  old_level: string
  new_level: string
  special_message: string
  unlocked_features: string[]
}

export interface InteractionAnalysisRequest {
  companion_id: number
  user_id: string
  message: string
  interaction_type?: string
}

export interface InteractionAnalysisResponse {
  sentiment: string
  user_intent: string
  topics: string[]
  affinity_change: number
  trust_change: number
  tension_change: number
  suggested_ai_mood: string
  memory_worthy: boolean
}

export interface DailyTaskResponse {
  task_id: string
  task_type: string
  description: string
  reward_affinity: number
  reward_coins?: number  // 金币奖励
  current_progress: number  // 当前进度
  max_progress: number  // 最大进度
  difficulty: 'easy' | 'medium' | 'hard' | 'challenge'  // 难度
  completed: boolean
  deadline: string | null
  milestones?: TaskMilestone[]  // 里程碑奖励
  reward_type?: 'affinity' | 'coins' | 'gems' | 'mixed'  // 奖励类型
}

export interface TaskMilestone {
  progress: number
  bonus: number
  type?: string
}

export interface StoreItemResponse {
  item_id: string
  item_type: string
  name: string
  description: string
  price: number
  currency: string
  preview_url: string | null
  rarity: string
  quantity?: number // 用户库存数量
  emoji?: string // 前端显示用的表情符号
}

export interface UserCurrencyResponse {
  coins: number
  gems: number
  daily_coins_earned: number
  daily_limit_reached: boolean
}

export interface CompanionChatContextRequest {
  companion_id: number
  user_id: string
  message: string
  session_id: string
  include_state?: boolean
  include_memories?: boolean
  include_recent_events?: boolean
}

export interface CompanionChatContextResponse {
  companion_name: string
  personality_archetype: string
  current_state: CompanionStateResponse
  relevant_memories: Memory[]
  recent_events: EventResponse[]
  suggested_response_tone: string
  relationship_context: string
}

// 前端特有的类型
export interface RomanceLevelConfig {
  name: string
  minAffinity: number
  maxAffinity: number
  color: string
  description: string
  unlocks: string[]
}

export interface MoodConfig {
  name: string
  emoji: string
  color: string
  description: string
}

export interface TaskTypeConfig {
  type: string
  icon: string
  color: string
  description: string
}

// 常量配置
export const ROMANCE_LEVELS: RomanceLevelConfig[] = [
  {
    name: '初识',
    minAffinity: 0,
    maxAffinity: 99,
    color: '#6b7280',
    description: '刚刚认识，保持礼貌距离',
    unlocks: ['基础对话']
  },
  {
    name: '朋友',
    minAffinity: 100,
    maxAffinity: 199,
    color: '#2563eb',
    description: '友好相处，可以聊各种话题',
    unlocks: ['日常分享', '兴趣交流']
  },
  {
    name: '好朋友',
    minAffinity: 200,
    maxAffinity: 349,
    color: '#059669',
    description: '深入了解，彼此信任',
    unlocks: ['深度话题', '情感支持']
  },
  {
    name: '特别的人',
    minAffinity: 350,
    maxAffinity: 499,
    color: '#d97706',
    description: '开始有特别的感觉',
    unlocks: ['暗示好感', '特殊关心']
  },
  {
    name: '心动',
    minAffinity: 500,
    maxAffinity: 699,
    color: '#e11d48',
    description: '怦然心动的感觉',
    unlocks: ['浪漫话题', '约会邀请']
  },
  {
    name: '恋人',
    minAffinity: 700,
    maxAffinity: 849,
    color: '#be185d',
    description: '确立恋爱关系',
    unlocks: ['情话甜言', '亲密称呼']
  },
  {
    name: '深爱',
    minAffinity: 850,
    maxAffinity: 1000,
    color: '#7c3aed',
    description: '深深相爱，感情深厚',
    unlocks: ['永恒承诺', '专属回忆']
  }
]

export const MOOD_CONFIGS: Record<string, MoodConfig> = {
  '平静': { name: '平静', emoji: '😐', color: '#6b7280', description: '心情平和' },
  '开心': { name: '开心', emoji: '😊', color: '#10b981', description: '心情愉悦' },
  '愉快': { name: '愉快', emoji: '🙂', color: '#3b82f6', description: '感觉不错' },
  '幸福': { name: '幸福', emoji: '😍', color: '#ec4899', description: '非常幸福' },
  '生气': { name: '生气', emoji: '😠', color: '#ef4444', description: '有些生气' },
  '委屈': { name: '委屈', emoji: '😢', color: '#8b5cf6', description: '感到委屈' },
  '困惑': { name: '困惑', emoji: '😕', color: '#f59e0b', description: '有点困惑' },
  '不安': { name: '不安', emoji: '😰', color: '#ef4444', description: '感到不安' }
}

export const GIFT_CONFIGS: Record<string, { emoji: string; affinity: number }> = {
  'flower': { emoji: '🌹', affinity: 15 },
  'chocolate': { emoji: '🍫', affinity: 10 },
  'jewelry': { emoji: '💎', affinity: 25 },
  'book': { emoji: '📚', affinity: 8 },
  'game': { emoji: '🎮', affinity: 12 },
  'outfit': { emoji: '👗', affinity: 20 },
  'teddy': { emoji: '🧸', affinity: 18 },
  'music': { emoji: '🎵', affinity: 12 },
  'food': { emoji: '🍰', affinity: 8 }
}
