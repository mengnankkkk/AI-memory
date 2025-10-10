/**
 * 好感度等级配置
 * 与后端 affinity_levels.py 保持一致
 */

export interface AffinityLevelConfig {
  key: string              // 英文键名 (与后端一致)
  name: string             // 中文显示名称
  minScore: number         // 最小分数
  maxScore: number         // 最大分数
  description: string      // 等级描述
  color: string            // 主题颜色
  bgColor: string          // 背景颜色
  icon: string             // 图标/表情
  avatarSuffix?: string    // 头像后缀 (用于组合角色ID)
}

/**
 * 7级好感度系统配置
 */
export const AFFINITY_LEVELS: Record<string, AffinityLevelConfig> = {
  stranger: {
    key: 'stranger',
    name: '陌生',
    minScore: 0,
    maxScore: 100,
    description: '刚刚认识，保持基本礼貌和距离感',
    color: '#6b7280',
    bgColor: '#e5e7eb',
    icon: '🤝',
    avatarSuffix: '_stranger'
  },
  acquaintance: {
    key: 'acquaintance',
    name: '认识',
    minScore: 101,
    maxScore: 250,
    description: '有了初步了解，可以进行基本交流',
    color: '#2563eb',
    bgColor: '#bfdbfe',
    icon: '👋',
    avatarSuffix: '_acquaintance'
  },
  friend: {
    key: 'friend',
    name: '朋友',
    minScore: 251,
    maxScore: 450,
    description: '建立了友谊，交流轻松自然',
    color: '#059669',
    bgColor: '#a7f3d0',
    icon: '😊',
    avatarSuffix: '_friend'
  },
  close_friend: {
    key: 'close_friend',
    name: '好友',
    minScore: 451,
    maxScore: 600,
    description: '深入了解，有较强的信任和默契',
    color: '#d97706',
    bgColor: '#fde68a',
    icon: '🤗',
    avatarSuffix: '_close_friend'
  },
  special: {
    key: 'special',
    name: '特别的人',
    minScore: 601,
    maxScore: 750,
    description: '对方变得特别，开始有微妙的情感',
    color: '#e11d48',
    bgColor: '#fbb6ce',
    icon: '💕',
    avatarSuffix: '_special'
  },
  romantic: {
    key: 'romantic',
    name: '心动',
    minScore: 751,
    maxScore: 900,
    description: '心动的感觉，但还未正式确认关系',
    color: '#be185d',
    bgColor: '#f9a8d4',
    icon: '💖',
    avatarSuffix: '_romantic'
  },
  lover: {
    key: 'lover',
    name: '恋人',
    minScore: 901,
    maxScore: 1000,
    description: '确认恋爱关系，深厚感情',
    color: '#7c3aed',
    bgColor: '#ddd6fe',
    icon: '💝',
    avatarSuffix: '_lover'
  }
}

/**
 * 等级顺序 (用于升降级判断)
 */
export const LEVEL_ORDER = [
  'stranger',
  'acquaintance',
  'friend',
  'close_friend',
  'special',
  'romantic',
  'lover'
]

/**
 * 根据分数获取等级
 */
export function getLevelByScore(score: number): AffinityLevelConfig {
  const clampedScore = Math.max(0, Math.min(1000, score))

  for (const key of LEVEL_ORDER) {
    const level = AFFINITY_LEVELS[key]
    if (clampedScore >= level.minScore && clampedScore <= level.maxScore) {
      return level
    }
  }

  return AFFINITY_LEVELS.stranger
}

/**
 * 根据等级键获取配置
 */
export function getLevelConfig(levelKey: string): AffinityLevelConfig {
  return AFFINITY_LEVELS[levelKey] || AFFINITY_LEVELS.stranger
}

/**
 * 获取等级进度百分比
 */
export function getLevelProgress(score: number, levelKey: string): number {
  const level = AFFINITY_LEVELS[levelKey]
  if (!level) return 0

  const range = level.maxScore - level.minScore
  const progress = score - level.minScore
  return Math.max(0, Math.min(100, (progress / range) * 100))
}

/**
 * 获取伙伴头像路径
 * @param companionId - 伙伴角色ID (如 'linzixi', 'kevin' 等)
 * @param levelKey - 等级键名 (如 'stranger', 'friend' 等)
 */
export function getCompanionAvatar(companionId: string, levelKey: string = 'stranger'): string {
  const level = AFFINITY_LEVELS[levelKey] || AFFINITY_LEVELS.stranger

  // 尝试获取等级特定头像
  const levelSpecificAvatar = `/img/${companionId}${level.avatarSuffix}.png`

  // 备用：基础头像
  const baseAvatar = `/img/${companionId}.png`

  // 返回路径（前端会尝试加载，失败则使用备用图）
  return levelSpecificAvatar
}

/**
 * 获取好感度变化的动画类型
 */
export function getAffinityChangeAnimation(delta: number): string {
  if (delta > 0) {
    if (delta >= 20) return 'big-increase'  // 大幅增加
    if (delta >= 10) return 'medium-increase'  // 中等增加
    return 'small-increase'  // 小幅增加
  } else if (delta < 0) {
    if (delta <= -20) return 'big-decrease'  // 大幅减少
    if (delta <= -10) return 'medium-decrease'  // 中等减少
    return 'small-decrease'  // 小幅减少
  }
  return 'no-change'
}

/**
 * 心情表情映射
 */
export const MOOD_EMOJIS: Record<string, string> = {
  '平静': '😐',
  '开心': '😊',
  '愉快': '🙂',
  '幸福': '😍',
  '生气': '😠',
  '委屈': '😢',
  '困惑': '😕',
  '不安': '😰',
  '兴奋': '🤩',
  '害羞': '😳',
  '期待': '✨'
}

/**
 * 伙伴角色配置
 */
export const COMPANION_PROFILES: Record<string, {
  id: string
  name: string
  archetype: string
  defaultGreeting: string
  traits: string[]
}> = {
  linzixi: {
    id: 'linzixi',
    name: '林紫溪',
    archetype: '古风才女',
    defaultGreeting: '公子安好，小女子有礼了~',
    traits: ['温婉', '知性', '古典美']
  },
  kevin: {
    id: 'kevin',
    name: '凯文',
    archetype: '铁哥们',
    defaultGreeting: '（理解地点点头）行，兄弟你先忙。工作要紧，bug要赶紧修，别到时候老板找你谈心了。(递给你一罐冰镇可乐)加油，等你有空了我们再聊游戏！',
    traits: ['热情', '直爽', '义气']
  },
  zoe: {
    id: 'zoe',
    name: '佐伊',
    archetype: '元气少女',
    defaultGreeting: '呀！是你呀！今天也要加油哦！',
    traits: ['活泼', '可爱', '正能量']
  },
  shiyu: {
    id: 'shiyu',
    name: '诗雨',
    archetype: '文艺女神',
    defaultGreeting: '又见面了，这个世界真美好~',
    traits: ['文艺', '浪漫', '敏感']
  },
  nagi: {
    id: 'nagi',
    name: '凪',
    archetype: '冷静学姐',
    defaultGreeting: '嗯，你来了。有什么问题吗？',
    traits: ['冷静', '聪明', '靠谱']
  },
  xuejian: {
    id: 'xuejian',
    name: '雪见',
    archetype: '治愈系',
    defaultGreeting: '欢迎回来~要不要喝杯茶？',
    traits: ['温柔', '体贴', '治愈']
  }
}
