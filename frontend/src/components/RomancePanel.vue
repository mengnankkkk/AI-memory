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
      <div class="tasks-header">
        <div class="header-left">
          <h4>今日任务</h4>
          <TaskBadge :count="incompleteTaskCount" :is-urgent="isTaskUrgent" />
        </div>
        <div class="completion-stats">
          <span class="completion-text">完成率</span>
          <span class="completion-value" :class="{ high: taskCompletionRate >= 80, medium: taskCompletionRate >= 50 && taskCompletionRate < 80 }">
            {{ taskCompletionRate }}%
          </span>
        </div>
      </div>

      <!-- 紧急任务提醒 -->
      <div v-if="isTaskUrgent" class="urgent-reminder">
        <i class="fas fa-exclamation-triangle"></i>
        <span>有 {{ urgentTasksCount }} 个任务即将过期！</span>
      </div>

      <div class="task-list">
        <div
          v-for="task in dailyTasks"
          :key="task.task_id"
          class="task-item"
          :class="{
            completed: task.completed,
            clickable: !task.completed,
            urgent: !task.completed && isTaskUrgentCheck(task),
            highlighted: !task.completed
          }"
          @click="completeTask(task)"
        >
          <div class="task-icon">
            <i :class="getTaskIcon(task.task_type)"></i>
          </div>
          <div class="task-content">
            <div class="task-header">
              <div class="task-description">{{ task.description }}</div>
              <div class="task-difficulty" :style="{ color: getDifficultyConfig(task.difficulty).color }">
                <span class="difficulty-icon">{{ getDifficultyConfig(task.difficulty).icon }}</span>
                <span class="difficulty-text">{{ getDifficultyConfig(task.difficulty).name }}</span>
              </div>
            </div>

            <!-- 进度条（仅多步骤任务） -->
            <TaskProgressBar
              v-if="hasProgress(task)"
              :current-progress="task.current_progress"
              :max-progress="task.max_progress"
              :milestones="task.milestones"
            />

            <div class="task-meta">
              <span class="task-reward">{{ getRewardText(task) }}</span>
              <span v-if="!task.completed && getTaskTimeRemaining(task)" class="task-deadline">
                {{ getTaskTimeRemaining(task) }}
              </span>
            </div>
          </div>
          <div class="task-status">
            <i v-if="task.completed" class="fas fa-check-circle"></i>
            <i v-else class="fas fa-circle task-uncompleted"></i>
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
          :class="{
            affordable: canAfford(gift),
            'out-of-stock': !gift.quantity || gift.quantity <= 0
          }"
          @click="selectGift(gift)"
        >
          <div class="gift-icon">{{ gift.emoji }}</div>
          <div class="gift-name">{{ gift.name }}</div>
          <div class="gift-quantity" :class="{ 'low-stock': gift.quantity && gift.quantity <= 2 }">
            库存: {{ gift.quantity || 0 }}
          </div>
          <div class="gift-rarity" :class="`rarity-${gift.rarity}`">
            {{ getRarityText(gift.rarity) }}
          </div>
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

    <!-- 礼物反馈弹窗 -->
    <GiftFeedback
      :visible="giftFeedback.visible"
      :gift-emoji="giftFeedback.giftEmoji"
      :gift-name="giftFeedback.giftName"
      :companion-reaction="giftFeedback.companionReaction"
      :affinity-change="giftFeedback.affinityChange"
      :old-affinity="giftFeedback.oldAffinity"
      :new-affinity="giftFeedback.newAffinity"
      @close="closeFeedback"
    />

    <!-- 等级提升闪卡 -->
    <LevelUpCard
      :visible="levelUpCard.visible"
      :companion-id="companionId"
      :companion-name="companionName"
      :old-level="levelUpCard.oldLevel"
      :new-level="levelUpCard.newLevel"
      :current-affinity="levelUpCard.currentAffinity"
      @close="closeLevelUpCard"
    />

    <!-- 任务完成反馈 -->
    <TaskFeedback
      :visible="taskFeedback.visible"
      :task-icon="taskFeedback.taskIcon"
      :task-description="taskFeedback.taskDescription"
      :reward="taskFeedback.reward"
      @close="closeTaskFeedback"
    />

    <!-- 新任务通知 -->
    <TaskNotification
      :visible="taskNotification.visible"
      :tasks="dailyTasks"
      @close="closeTaskNotification"
      @go-to-tasks="scrollToTasks"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { romanceApi } from '@/services/romance'
import GiftFeedback from './GiftFeedback.vue'
import LevelUpCard from './LevelUpCard.vue'
import TaskFeedback from './TaskFeedback.vue'
import TaskBadge from './TaskBadge.vue'
import TaskNotification from './TaskNotification.vue'
import TaskProgressBar from './TaskProgressBar.vue'
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

// 礼物反馈数据
const giftFeedback = ref({
  visible: false,
  giftEmoji: '🎁',
  giftName: '',
  companionReaction: '',
  affinityChange: 0,
  oldAffinity: 0,
  newAffinity: 0
})

// 等级提升卡片数据
const levelUpCard = ref({
  visible: false,
  oldLevel: 'stranger',
  newLevel: 'stranger',
  currentAffinity: 0
})

// 任务完成反馈数据
const taskFeedback = ref({
  visible: false,
  taskIcon: '⭐',
  taskDescription: '',
  reward: 0
})

// 新任务通知
const taskNotification = ref({
  visible: false
})

// 上次任务检查日期（用于检测新的一天）
const lastTaskCheckDate = ref<string | null>(null)

// 记录上次的等级
const previousLevel = ref<string | null>(null)

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

// 任务相关计算属性
const incompleteTasks = computed(() => {
  return dailyTasks.value.filter(task => !task.completed)
})

const incompleteTaskCount = computed(() => {
  return incompleteTasks.value.length
})

const taskCompletionRate = computed(() => {
  if (dailyTasks.value.length === 0) return 0
  const completed = dailyTasks.value.filter(task => task.completed).length
  return Math.round((completed / dailyTasks.value.length) * 100)
})

const isTaskUrgent = computed(() => {
  // 检查是否有任务快过期（剩余时间<6小时）
  const now = new Date()
  return incompleteTasks.value.some(task => {
    const deadline = new Date(task.deadline)
    const hoursRemaining = (deadline.getTime() - now.getTime()) / (1000 * 60 * 60)
    return hoursRemaining > 0 && hoursRemaining < 6
  })
})

const urgentTasksCount = computed(() => {
  const now = new Date()
  return incompleteTasks.value.filter(task => {
    const deadline = new Date(task.deadline)
    const hoursRemaining = (deadline.getTime() - now.getTime()) / (1000 * 60 * 60)
    return hoursRemaining > 0 && hoursRemaining < 6
  }).length
})

// 方法
const loadCompanionState = async () => {
  try {
    loading.value = true
    const newState = await romanceApi.getCompanionState(props.companionId, props.userId)

    // 检测等级变化
    if (companionState.value && previousLevel.value) {
      const oldLevel = companionState.value.romance_level
      const newLevel = newState.romance_level

      // 如果等级提升了，显示闪卡
      if (oldLevel !== newLevel && !isFirstLoad(oldLevel, newLevel)) {
        levelUpCard.value = {
          visible: true,
          oldLevel: oldLevel,
          newLevel: newLevel,
          currentAffinity: newState.affinity_score
        }
      }
    }

    // 更新状态
    companionState.value = newState
    previousLevel.value = newState.romance_level
  } catch (error) {
    console.error('加载伙伴状态失败:', error)
  } finally {
    loading.value = false
  }
}

// 判断是否是首次加载（避免初始化时显示闪卡）
const isFirstLoad = (oldLevel: string, newLevel: string): boolean => {
  // 如果previousLevel为null，说明是首次加载
  return previousLevel.value === null
}

const loadDailyTasks = async () => {
  try {
    dailyTasks.value = await romanceApi.getDailyTasks(props.companionId, props.userId)

    // 检测是否是新的一天
    const today = new Date().toDateString()
    if (lastTaskCheckDate.value !== today && dailyTasks.value.length > 0) {
      // 如果有未完成的任务，显示通知
      const hasIncompleteTasks = dailyTasks.value.some(task => !task.completed)
      if (hasIncompleteTasks && lastTaskCheckDate.value !== null) {
        // 延迟1秒显示通知，避免页面加载时立即弹出
        setTimeout(() => {
          taskNotification.value.visible = true
        }, 1000)
      }
      lastTaskCheckDate.value = today
      // 保存到localStorage
      localStorage.setItem(`lastTaskCheck_${props.companionId}_${props.userId}`, today)
    }
  } catch (error) {
    console.error('加载每日任务失败:', error)
  }
}

const loadGifts = async () => {
  try {
    console.log('[RomancePanel] 开始加载礼物列表, userId:', props.userId)
    const gifts = await romanceApi.getStoreItems(props.userId, 'gift')
    console.log('[RomancePanel] 礼物列表加载成功:', gifts.length, '个礼物')
    console.log('[RomancePanel] 礼物详情:', gifts)
    availableGifts.value = gifts
  } catch (error) {
    console.error('[RomancePanel] 加载礼物列表失败:', error)
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
  // 检查库存
  if (!gift.quantity || gift.quantity <= 0) {
    alert('库存不足！请等待补货或购买更多礼物')
    return
  }

  try {
    // 保存赠送前的好感度
    const oldAffinity = companionState.value?.affinity_score || 0

    const response = await romanceApi.giveGift(props.companionId, {
      gift_type: gift.item_id,
      gift_name: gift.name,
      user_id: props.userId
    })

    if (response.success) {
      // 显示礼物反馈动画
      giftFeedback.value = {
        visible: true,
        giftEmoji: gift.emoji || '🎁',
        giftName: gift.name,
        companionReaction: response.companion_reaction,
        affinityChange: response.affinity_change,
        oldAffinity: oldAffinity,
        newAffinity: response.new_affinity_score
      }

      // 刷新状态和礼物列表
      await Promise.all([
        loadCompanionState(),
        loadGifts()
      ])
    }
  } catch (error: any) {
    console.error('赠送礼物失败:', error)
    const errorMsg = error.response?.data?.detail || '赠送失败，请稍后重试'
    alert(errorMsg)
  }
}

const closeFeedback = () => {
  giftFeedback.value.visible = false
}

const closeLevelUpCard = () => {
  levelUpCard.value.visible = false
}

const closeTaskFeedback = () => {
  taskFeedback.value.visible = false
}

const closeTaskNotification = () => {
  taskNotification.value.visible = false
}

const scrollToTasks = () => {
  // 滚动到任务区域
  const tasksSection = document.querySelector('.daily-tasks')
  if (tasksSection) {
    tasksSection.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const getTaskTimeRemaining = (task: DailyTaskResponse): string => {
  const now = new Date()
  const deadline = new Date(task.deadline)
  const hoursRemaining = (deadline.getTime() - now.getTime()) / (1000 * 60 * 60)

  if (hoursRemaining < 0) return '已过期'
  if (hoursRemaining < 1) return `${Math.round(hoursRemaining * 60)}分钟内过期`
  if (hoursRemaining < 6) return `${Math.round(hoursRemaining)}小时内过期`
  return ''
}

const isTaskUrgentCheck = (task: DailyTaskResponse): boolean => {
  const now = new Date()
  const deadline = new Date(task.deadline)
  const hoursRemaining = (deadline.getTime() - now.getTime()) / (1000 * 60 * 60)
  return hoursRemaining > 0 && hoursRemaining < 6
}

const completeTask = async (task: DailyTaskResponse) => {
  // 检查任务是否已完成
  if (task.completed) {
    return
  }

  try {
    const response = await romanceApi.completeTask(props.companionId, task.task_id, props.userId)

    if (response.success) {
      // 显示任务完成反馈
      taskFeedback.value = {
        visible: true,
        taskIcon: getTaskIconEmoji(task.task_type),
        taskDescription: task.description,
        reward: response.reward
      }

      // 刷新状态和任务列表
      await Promise.all([
        loadCompanionState(),
        loadDailyTasks()
      ])
    }
  } catch (error: any) {
    console.error('完成任务失败:', error)
    const errorMsg = error.response?.data?.detail || '任务完成失败，请稍后重试'
    alert(errorMsg)
  }
}

const getTaskIconEmoji = (taskType: string): string => {
  const emojiMap: Record<string, string> = {
    'chat': '💬',
    'compliment': '💖',
    'romantic': '💕',
    'gift': '🎁'
  }
  return emojiMap[taskType] || '⭐'
}

const getRarityText = (rarity: string): string => {
  const rarityMap: Record<string, string> = {
    'common': '普通',
    'rare': '稀有',
    'epic': '史诗',
    'legendary': '传说'
  }
  return rarityMap[rarity] || rarity
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

const getDifficultyConfig = (difficulty: string) => {
  const configs = {
    'easy': { name: '简单', color: '#10b981', icon: '⭐' },
    'medium': { name: '中等', color: '#3b82f6', icon: '⭐⭐' },
    'hard': { name: '困难', color: '#f59e0b', icon: '⭐⭐⭐' },
    'challenge': { name: '挑战', color: '#ef4444', icon: '⭐⭐⭐⭐' }
  }
  return configs[difficulty] || configs['easy']
}

const hasProgress = (task: DailyTaskResponse): boolean => {
  return task.max_progress > 1
}

const getRewardText = (task: DailyTaskResponse): string => {
  const rewards = []
  if (task.reward_affinity) {
    rewards.push(`+${task.reward_affinity} 好感度`)
  }
  if (task.reward_coins) {
    rewards.push(`+${task.reward_coins} 金币`)
  }
  return rewards.join(' | ')
}

// 生命周期
onMounted(async () => {
  console.log('[RomancePanel] 组件挂载, props:', props)

  // 从localStorage恢复上次检查日期
  const savedDate = localStorage.getItem(`lastTaskCheck_${props.companionId}_${props.userId}`)
  if (savedDate) {
    lastTaskCheckDate.value = savedDate
  }

  await Promise.all([
    loadCompanionState(),
    loadDailyTasks(),
    loadGifts(),
    loadPendingEvents(),
    loadUserCurrency()
  ])
  console.log('[RomancePanel] 所有数据加载完成, availableGifts:', availableGifts.value.length, '个')
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

.tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h4 {
  margin: 0;
}

.completion-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.8);
  padding: 8px 16px;
  border-radius: 20px;
}

.completion-text {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 600;
}

.completion-value {
  font-size: 1rem;
  font-weight: 700;
  color: #6b7280;
}

.completion-value.medium {
  color: #f59e0b;
}

.completion-value.high {
  color: #10b981;
}

.urgent-reminder {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid #fbbf24;
  animation: urgentPulse 2s ease-in-out infinite;
}

@keyframes urgentPulse {
  0%, 100% {
    box-shadow: 0 0 0 rgba(251, 191, 36, 0);
  }
  50% {
    box-shadow: 0 0 16px rgba(251, 191, 36, 0.5);
  }
}

.urgent-reminder i {
  color: #d97706;
  font-size: 1.125rem;
}

.urgent-reminder span {
  color: #92400e;
  font-weight: 600;
  font-size: 0.875rem;
}

.task-list, .event-list, .memories-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  transition: all 0.2s ease;
}

.task-item.clickable {
  cursor: pointer;
}

.task-item.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(107, 70, 193, 0.2);
  border-color: #a78bfa;
}

.task-item:hover, .event-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(107, 70, 193, 0.2);
}

.event-item {
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

.task-item.completed {
  opacity: 0.6;
  background: #f0fdf4;
  cursor: not-allowed;
}

.task-item.completed:hover {
  transform: none;
  box-shadow: none;
  border-color: rgba(255, 255, 255, 0.9);
}

.task-item.highlighted:not(.completed) {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-color: #a78bfa;
}

.task-item.urgent:not(.completed) {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.15) 100%);
  border-color: #f59e0b;
  animation: urgentShake 3s ease-in-out infinite;
}

@keyframes urgentShake {
  0%, 98%, 100% {
    transform: translateX(0);
  }
  99%, 99.5% {
    transform: translateX(-2px);
  }
  99.25%, 99.75% {
    transform: translateX(2px);
  }
}

.task-content {
  flex: 1;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.task-description {
  flex: 1;
  font-size: 0.9375rem;
  color: #374151;
  font-weight: 500;
}

.task-difficulty {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.difficulty-icon {
  font-size: 0.65rem;
}

.difficulty-text {
  font-size: 0.7rem;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.task-reward {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 600;
}

.task-deadline {
  font-size: 0.75rem;
  color: #f59e0b;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-deadline::before {
  content: '⏰';
}

.task-uncompleted {
  color: #d1d5db;
  font-size: 0.875rem;
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

.gift-item.out-of-stock {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(0.8);
}

.gift-item.out-of-stock:hover {
  transform: none;
  box-shadow: none;
}

.gift-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.gift-name {
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 4px;
  font-weight: 500;
}

.gift-quantity {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 500;
  margin-bottom: 4px;
}

.gift-quantity.low-stock {
  color: #f59e0b;
  font-weight: 600;
}

.gift-rarity {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.rarity-common {
  background: #e5e7eb;
  color: #6b7280;
}

.rarity-rare {
  background: #bfdbfe;
  color: #2563eb;
}

.rarity-epic {
  background: #f9a8d4;
  color: #be185d;
}

.rarity-legendary {
  background: #fde68a;
  color: #d97706;
  animation: legendary-glow 2s infinite;
}

@keyframes legendary-glow {
  0%, 100% { box-shadow: 0 0 5px rgba(217, 119, 6, 0.5); }
  50% { box-shadow: 0 0 15px rgba(217, 119, 6, 0.8); }
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
