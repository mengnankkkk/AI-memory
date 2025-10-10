<template>
  <div class="romance-panel">
    <!-- 关系状态显示 -->
    <div class="relationship-status">
      <div class="status-header">
        <h3>{{ companionName }} 的心意</h3>
        <div class="romance-level" :class="romanceLevelClass">
          {{ companionState ? getLevelConfig(companionState.romance_level).name : '初始化中' }}
        </div>
      </div>
      
      <!-- 好感度进度条 -->
      <div class="affinity-bar">
        <div class="affinity-label">
          <span>好感度</span>
          <span>{{ companionState?.affinity_score }}/1000</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: affinityPercentage + '%' }"
            :class="affinityLevelClass"
          ></div>
        </div>
      </div>
      
      <!-- 当前心情 -->
      <div class="mood-indicator">
        <div class="mood-emoji" :class="moodClass">{{ moodEmoji }}</div>
        <span class="mood-text">{{ companionState?.current_mood }}</span>
      </div>
      
      <!-- 关系统计 -->
      <div class="relationship-stats">
        <div class="stat-item">
          <span class="stat-label">交流次数</span>
          <span class="stat-value">{{ companionState?.total_interactions }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">信任度</span>
          <span class="stat-value">{{ companionState?.trust_score }}/100</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">相识天数</span>
          <span class="stat-value">{{ companionState?.days_since_first_meet }}</span>
        </div>
      </div>
    </div>

    <!-- 每日任务 -->
    <div class="daily-tasks" v-if="dailyTasks && dailyTasks.length > 0">
      <h4>今日任务</h4>
      <div class="task-list">
        <div 
          v-for="task in dailyTasks" 
          :key="task.task_id"
          class="task-item"
          :class="{ completed: task.completed }"
        >
          <div class="task-icon">
            <i :class="getTaskIcon(task.task_type)"></i>
          </div>
          <div class="task-content">
            <div class="task-description">{{ task.description }}</div>
            <div class="task-reward">+{{ task.reward_affinity }} 好感度</div>
          </div>
          <div class="task-status">
            <i v-if="task.completed" class="fas fa-check-circle"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- 礼物赠送 -->
    <div class="gift-section">
      <h4>赠送礼物</h4>
      <div class="gift-grid">
        <div 
          v-for="gift in availableGifts" 
          :key="gift.item_id"
          class="gift-item"
          :class="{ affordable: canAfford(gift) }"
          @click="selectGift(gift)"
        >
          <div class="gift-icon">{{ gift.emoji }}</div>
          <div class="gift-name">{{ gift.name }}</div>
          <div class="gift-price">{{ gift.price }} 💰</div>
        </div>
      </div>
    </div>

    <!-- 待处理事件 -->
    <div class="pending-events" v-if="pendingEvents && pendingEvents.length > 0">
      <h4>特殊事件</h4>
      <div class="event-list">
        <div 
          v-for="event in pendingEvents" 
          :key="event.type"
          class="event-item"
          @click="handleEvent(event)"
        >
          <div class="event-icon">💝</div>
          <div class="event-content">
            <div class="event-title">{{ event.title }}</div>
            <div class="event-description">{{ event.description }}</div>
          </div>
          <div class="event-arrow">
            <i class="fas fa-chevron-right"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- 记忆片段 -->
    <div class="memories-section" v-if="recentMemories && recentMemories.length > 0">
      <h4>珍贵回忆</h4>
      <div class="memories-list">
        <div 
          v-for="memory in recentMemories" 
          :key="memory.timestamp"
          class="memory-item"
        >
          <div class="memory-content">{{ memory.content }}</div>
          <div class="memory-time">{{ formatMemoryTime(memory.timestamp) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { romanceApi } from '@/services/romance'
import type {
  CompanionStateResponse,
  DailyTaskResponse,
  StoreItemResponse,
  EventResponse
} from '@/types/romance'
import { getLevelConfig, MOOD_EMOJIS } from '@/config/affinity-config'

interface Props {
  companionId: number
  companionName: string
  userId: string
}

const props = defineProps<Props>()

// 响应式数据
const companionState = ref<CompanionStateResponse | null>(null)
const dailyTasks = ref<DailyTaskResponse[]>([])
const availableGifts = ref<StoreItemResponse[]>([])
const pendingEvents = ref<EventResponse[]>([])
const userCurrency = ref({ coins: 0, gems: 0 })
const loading = ref(false)

// 计算属性
const affinityPercentage = computed(() => {
  if (!companionState.value) return 0
  return (companionState.value.affinity_score / 1000) * 100
})

const romanceLevelClass = computed(() => {
  if (!companionState.value) return ''
  const levelKey = companionState.value.romance_level
  const levelConfig = getLevelConfig(levelKey)

  // 使用配置中的颜色类名
  return `level-${levelKey}`
})

const affinityLevelClass = computed(() => {
  if (!companionState.value) return ''
  const score = companionState.value.affinity_score
  if (score < 200) return 'affinity-low'
  if (score < 500) return 'affinity-medium'
  if (score < 800) return 'affinity-high'
  return 'affinity-max'
})

const moodClass = computed(() => {
  if (!companionState.value) return ''
  return `mood-${companionState.value.current_mood}`
})

const moodEmoji = computed(() => {
  if (!companionState.value) return '😐'
  return MOOD_EMOJIS[companionState.value.current_mood] || '😐'
})

const recentMemories = computed(() => {
  if (!companionState.value?.memories) return []
  return companionState.value.memories
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, 3)
})

// 方法
const loadCompanionState = async () => {
  try {
    loading.value = true
    companionState.value = await romanceApi.getCompanionState(props.companionId, props.userId)
  } catch (error) {
    console.error('加载伙伴状态失败:', error)
  } finally {
    loading.value = false
  }
}

const loadDailyTasks = async () => {
  try {
    dailyTasks.value = await romanceApi.getDailyTasks(props.companionId, props.userId)
  } catch (error) {
    console.error('加载每日任务失败:', error)
  }
}

const loadGifts = async () => {
  try {
    availableGifts.value = await romanceApi.getStoreItems('gift')
  } catch (error) {
    console.error('加载礼物列表失败:', error)
  }
}

const loadPendingEvents = async () => {
  try {
    const response = await romanceApi.getPendingEvents(props.companionId, props.userId)
    pendingEvents.value = response.events || []
  } catch (error) {
    console.error('加载待处理事件失败:', error)
  }
}

const loadUserCurrency = async () => {
  try {
    userCurrency.value = await romanceApi.getUserCurrency(props.userId)
  } catch (error) {
    console.error('加载用户货币失败:', error)
  }
}

const selectGift = async (gift: StoreItemResponse) => {
  if (!canAfford(gift)) {
    alert('金币不足！')
    return
  }

  try {
    // 从item_id中提取gift_type（如 "flower_rose" -> "flower"）
    const giftType = gift.item_id.split('_')[0]

    const response = await romanceApi.giveGift(props.companionId, {
      gift_type: giftType,
      gift_name: gift.name,
      user_id: props.userId
    })
    
    if (response.success) {
      alert(`${response.companion_reaction}`)
      // 刷新状态
      await Promise.all([
        loadCompanionState(),
        loadUserCurrency()
      ])
    }
  } catch (error) {
    console.error('赠送礼物失败:', error)
    alert('赠送失败，请稍后重试')
  }
}

const handleEvent = async (event: EventResponse) => {
  // 处理特殊事件
  alert(`触发了特殊事件: ${event.title}`)
  // 这里可以跳转到特殊事件页面或显示事件对话
}

const canAfford = (gift: StoreItemResponse): boolean => {
  if (gift.currency === 'coins') {
    return userCurrency.value.coins >= gift.price
  } else if (gift.currency === 'gems') {
    return userCurrency.value.gems >= gift.price
  }
  return false
}

const getTaskIcon = (taskType: string): string => {
  const iconMap: Record<string, string> = {
    'chat': 'fas fa-comments',
    'compliment': 'fas fa-heart',
    'romantic': 'fas fa-kiss-wink-heart',
    'gift': 'fas fa-gift'
  }
  return iconMap[taskType] || 'fas fa-star'
}

const formatMemoryTime = (timestamp: number): string => {
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '昨天'
  if (diffDays < 7) return `${diffDays}天前`
  return date.toLocaleDateString()
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadCompanionState(),
    loadDailyTasks(),
    loadGifts(),
    loadPendingEvents(),
    loadUserCurrency()
  ])
})

// 监听 companionId 变化
watch(() => props.companionId, async () => {
  await loadCompanionState()
  await loadDailyTasks()
  await loadPendingEvents()
})

// 每5分钟刷新一次状态
setInterval(() => {
  loadCompanionState()
  loadPendingEvents()
}, 5 * 60 * 1000)
</script>

<style scoped>
.romance-panel {
  background: linear-gradient(135deg, #ffeef8 0%, #f8f3ff 100%);
  border-radius: 20px;
  padding: 24px;
  margin: 16px 0;
  box-shadow: 0 8px 32px rgba(255, 182, 235, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.relationship-status {
  margin-bottom: 24px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.status-header h3 {
  margin: 0;
  color: #6b46c1;
  font-size: 1.25rem;
}

.romance-level {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.level-stranger { background: #e5e7eb; color: #6b7280; }
.level-acquaintance { background: #bfdbfe; color: #2563eb; }
.level-friend { background: #a7f3d0; color: #059669; }
.level-close_friend { background: #fde68a; color: #d97706; }
.level-special { background: #fbb6ce; color: #e11d48; }
.level-romantic { background: #f9a8d4; color: #be185d; }
.level-lover { background: #ddd6fe; color: #7c3aed; }

.affinity-bar {
  margin-bottom: 16px;
}

.affinity-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.875rem;
  color: #6b7280;
}

.progress-bar {
  height: 12px;
  background: #f3f4f6;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 6px;
}

.affinity-low { background: linear-gradient(90deg, #fee2e2, #fecaca); }
.affinity-medium { background: linear-gradient(90deg, #fed7d7, #f9a8d4); }
.affinity-high { background: linear-gradient(90deg, #f9a8d4, #c084fc); }
.affinity-max { background: linear-gradient(90deg, #c084fc, #a855f7); }

.mood-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.mood-emoji {
  font-size: 2rem;
  animation: pulse 2s infinite;
}

.mood-text {
  font-size: 1.125rem;
  color: #374151;
  font-weight: 500;
}

.relationship-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
}

.daily-tasks, .gift-section, .pending-events, .memories-section {
  margin-bottom: 24px;
}

.daily-tasks h4, .gift-section h4, .pending-events h4, .memories-section h4 {
  margin: 0 0 16px 0;
  color: #6b46c1;
  font-size: 1.125rem;
}

.task-list, .event-list, .memories-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item, .event-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-item:hover, .event-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(107, 70, 193, 0.2);
}

.task-item.completed {
  opacity: 0.6;
  background: #f0fdf4;
}

.gift-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
}

.gift-item {
  text-align: center;
  padding: 16px 8px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.2s ease;
}

.gift-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(107, 70, 193, 0.2);
}

.gift-item.affordable {
  border-color: #10b981;
}

.gift-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.gift-name {
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 4px;
}

.gift-price {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.memory-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.9);
}

.memory-content {
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 4px;
}

.memory-time {
  font-size: 0.75rem;
  color: #6b7280;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@media (max-width: 768px) {
  .relationship-stats {
    grid-template-columns: 1fr;
  }
  
  .gift-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
