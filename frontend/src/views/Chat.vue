<script setup lang="ts">
import { ref, onMounted, nextTick, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { companionService } from '@/services/companion'
import { useUserStore } from '@/stores/user'
import { useWebSocketChat } from '@/services/websocket'
import RomancePanel from '@/components/RomancePanel.vue'
import CompanionAvatar from '@/components/CompanionAvatar.vue'
import EventCard from '@/components/EventCard.vue'
import type { Companion, ChatMessage } from '@/types'
import api from '@/services/auth'
import { romanceApi } from '@/services/romance'
import { getLevelConfig, getLevelProgress, type AffinityLevelConfig } from '@/config/affinity-config'
import { eventApi, type EventData } from '@/services/event'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const {
  isConnected,
  isConnecting,
  currentStreamingMessage,
  connect,
  disconnect,
  joinChat,
  sendMessage: sendSocketMessage,
  setAutoJoinCallback,
  onMessageReceived,
  onResponseStart,
  onResponseChunk,
  onResponseEnd,
  onError,
  onChatJoined,
  onTasksCompleted,
  removeAllListeners
} = useWebSocketChat()

const companionId = Number(route.params.companionId)

const companion = ref<Companion | null>(null)
const messages = ref<ChatMessage[]>([])
const userInput = ref('')
const isLoading = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
const currentChatSession = ref<any>(null)
const connectionStatus = ref('连接中...')
const showRomancePanel = ref(false) // 控制恋爱攻略面板显示
const affinityScore = ref<number | null>(null)
const romanceLevel = ref<string>('')
const showAffinityChange = ref(false)
const affinityDelta = ref(0)
let affinityTimeout: ReturnType<typeof setTimeout> | null = null
const romancePanelRef = ref<any>(null) // RomancePanel组件引用

// 事件系统相关状态
const pendingEvents = ref<EventData[]>([])
const currentEvent = ref<EventData | null>(null)

// 计算等级配置
const levelConfig = computed<AffinityLevelConfig | null>(() => {
  if (!romanceLevel.value) return null
  return getLevelConfig(romanceLevel.value)
})

// 计算当前等级进度
const levelProgress = computed(() => {
  if (!affinityScore.value || !romanceLevel.value) return 0
  return getLevelProgress(affinityScore.value, romanceLevel.value)
})

// 加载伙伴信息和聊天历史
const loadCompanion = async () => {
  try {
    companion.value = await companionService.get(companionId)
    
    // 从用户store查找对应的伙伴信息
    const storeCompanion = userStore.companions.find(c => c.id === companionId)
    if (storeCompanion) {
      userStore.setCurrentCompanion(storeCompanion)
    }
    
    // 添加问候消息
    messages.value.push({
      role: 'assistant',
      content: companion.value.greeting || '你好！我是你的AI伙伴，很高兴认识你！'
    })
    
    await loadCompanionState()

    // 加载聊天会话历史
    await loadChatHistory()
    
  } catch (error) {
    console.error('加载失败:', error)
    alert('无法加载伙伴信息')
    router.push({ name: 'home' })
  }
}

const loadCompanionState = async () => {
  try {
    if (!companion.value) return
    const state = await romanceApi.getCompanionState(companionId, userStore.userId || 'default')
    affinityScore.value = state.affinity_score
    romanceLevel.value = state.romance_level
  } catch (error) {
    console.error('加载伙伴状态失败:', error)
  }
}

const refreshAffinityState = async () => {
  try {
    if (!companion.value) return
    const prev = affinityScore.value
    await loadCompanionState()
    if (prev !== null && affinityScore.value !== null) {
      const delta = affinityScore.value - prev
      if (delta !== 0) {
        affinityDelta.value = delta
        showAffinityChange.value = true
        if (affinityTimeout) {
          clearTimeout(affinityTimeout)
        }
        affinityTimeout = setTimeout(() => {
          showAffinityChange.value = false
        }, 1500)
      }
    }
    // 刷新好感度后检查事件
    await loadPendingEvents()
  } catch (error) {
    console.error('刷新好感度失败:', error)
  }
}

// 加载待处理事件
const loadPendingEvents = async () => {
  try {
    const events = await eventApi.getPendingEvents(companionId)
    pendingEvents.value = events

    // 如果有未完成的事件，显示第一个
    if (events.length > 0 && !currentEvent.value) {
      currentEvent.value = events[0]
      // 设置companion_name
      if (companion.value) {
        currentEvent.value.companion_name = companion.value.name
      }
    }
  } catch (error) {
    console.error('加载事件失败:', error)
  }
}

// 处理事件交互
const handleEventInteract = async (historyId: number) => {
  if (!currentEvent.value) return

  // 将事件注入到对话上下文
  const eventContext = `[刚才发生的事情] ${currentEvent.value.script_content.description.replace(/\{name\}/g, companion.value?.name || '伙伴')}`
  userInput.value = `${eventContext}\n\n我想和你聊聊这件事...`

  // 标记事件为已完成
  try {
    await eventApi.completeEvent(historyId, 'conversation_triggered')
    pendingEvents.value = pendingEvents.value.filter(e => e.history_id !== historyId)
    currentEvent.value = pendingEvents.value[0] || null
    if (currentEvent.value && companion.value) {
      currentEvent.value.companion_name = companion.value.name
    }
  } catch (error) {
    console.error('完成事件失败:', error)
  }

  // 发送消息
  await sendMessage()
}

// 关闭事件卡片
const closeEventCard = async () => {
  if (currentEvent.value) {
    try {
      await eventApi.completeEvent(currentEvent.value.history_id, 'dismissed')
      pendingEvents.value = pendingEvents.value.filter(
        e => e.history_id !== currentEvent.value!.history_id
      )
      currentEvent.value = pendingEvents.value[0] || null
      if (currentEvent.value && companion.value) {
        currentEvent.value.companion_name = companion.value.name
      }
    } catch (error) {
      console.error('关闭事件失败:', error)
    }
  }
}

// 加载聊天历史
const loadChatHistory = async () => {
  try {
    // 获取该伙伴的会话历史
    await userStore.loadChatSessions(companionId)
    
    if (userStore.chatSessions.length > 0) {
      // 使用最新的会话
      const latestSession = userStore.chatSessions[0]
      currentChatSession.value = latestSession
      userStore.setCurrentSession(latestSession)
      
      // 加载该会话的消息历史
      await userStore.loadChatMessages(latestSession.id)
      
      // 将历史消息添加到当前消息列表
      if (userStore.chatMessages.length > 0) {
        // 清空问候消息，用历史消息替换
        messages.value = [...userStore.chatMessages]
      }
    } else {
      // 创建新会话
      const newSession = await userStore.createChatSession(
        companionId,
        `与${companion.value?.name}的对话`
      )
      if (newSession) {
        console.log('🔍 创建新会话调试信息:', {
          newSession,
          sessionId: newSession.id
        })
        currentChatSession.value = newSession
        userStore.setCurrentSession(newSession)
      }
    }
  } catch (error) {
    console.error('加载聊天历史失败:', error)
  }
}

// 初始化WebSocket连接
const initWebSocket = () => {
  connect()
  
  // 监听连接状态
  onChatJoined((data) => {
    console.log('✅ 成功加入聊天:', data)
    connectionStatus.value = '已连接'
  })
  
  // 设置自动加入回调
  setAutoJoinCallback(() => {
    console.log('🔗 WebSocket连接成功，准备加入聊天...')
    if (userStore.userId && currentChatSession.value) {
      console.log('🔗 加入聊天:', { companionId, userId: userStore.userId, chatSessionId: currentChatSession.value.id })
      joinChat(companionId, userStore.userId, currentChatSession.value.id)
    }
  })
  
  // 监听消息确认
  onMessageReceived((message) => {
    console.log('📨 消息已接收:', message)
  })
  
  // 监听流式响应开始
  onResponseStart(() => {
    console.log('🚀 开始接收流式响应')
    // 添加一个空的助手消息用于流式更新
    messages.value.push({
      role: 'assistant',
      content: ''
    })
    scrollToBottom()
  })
  
  // 监听流式响应块
  onResponseChunk((chunk) => {
    // 更新最后一条助手消息
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage && lastMessage.role === 'assistant') {
      lastMessage.content += chunk
      scrollToBottom()
    }
  })
  
  // 监听流式响应结束
  onResponseEnd(async (fullContent) => {
    console.log('✅ 流式响应完成:', fullContent)
    // 确保最后一条消息内容正确
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage && lastMessage.role === 'assistant') {
      lastMessage.content = fullContent

      // 保存消息到用户store
      userStore.addChatMessage({
        id: Date.now(),
        role: 'assistant',
        content: fullContent,
        timestamp: new Date().toISOString()
      })
    }
    isLoading.value = false
    await refreshAffinityState()
  })

  // 监听任务完成
  onTasksCompleted(async (data) => {
    console.log('✅ 任务完成通知:', data)
    // 刷新好感度状态
    await refreshAffinityState()
    // 刷新RomancePanel中的任务列表
    if (romancePanelRef.value && romancePanelRef.value.loadDailyTasks) {
      await romancePanelRef.value.loadDailyTasks()
      console.log('🔄 已刷新任务列表')
    }
  })

  // 监听错误
  onError((error) => {
    console.error('❌ 聊天错误:', error)
    alert(`聊天错误: ${error.message}`)
    isLoading.value = false
  })
  
  // 连接成功后加入聊天
  const checkAndJoinChat = () => {
    if (isConnected.value && companionId && currentChatSession.value) {
      joinChat(
        companionId,
        userStore.userId,
        currentChatSession.value.id
      )
    } else {
      // 等待连接或数据加载完成后重试
      setTimeout(checkAndJoinChat, 1000)
    }
  }
  
  setTimeout(checkAndJoinChat, 1000)
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value || !isConnected.value) return

  const message = userInput.value.trim()
  userInput.value = ''

  // 添加用户消息
  const userMessage = {
    role: 'user' as const,
    content: message,
    timestamp: new Date().toISOString()
  }
  
  messages.value.push(userMessage)
  
  // 保存用户消息到store
  userStore.addChatMessage({
    id: Date.now(),
    ...userMessage
  })
  
  scrollToBottom()

  isLoading.value = true
  
  try {
    // 通过WebSocket发送消息，传递当前会话ID
    console.log('🔍 发送消息调试信息:', {
      message,
      currentChatSession: currentChatSession.value,
      sessionId: currentChatSession.value?.id
    })
    sendSocketMessage(message, currentChatSession.value?.id)
  } catch (error) {
    console.error('发送失败:', error)
    alert('消息发送失败,请重试')
    isLoading.value = false
  }
}

// 重新连接WebSocket
const reconnectWebSocket = () => {
  disconnect()
  setTimeout(() => {
    initWebSocket()
  }, 1000)
}

// 跳转到伙伴设置页
function goToSettings() {
  if (companion.value && companion.value.id) {
    router.push({ name: 'settings', params: { companionId: companion.value.id } })
  }
}

// 反馈消息
async function feedback(msg: ChatMessage, score: number) {
  try {
    if (!msg.id || !companion.value) return
    await api.post('/chat/feedback', {
      companion_id: companion.value.id,
      message_id: msg.id,
      score
    })
    alert('反馈已提交')
  } catch (e) {
    alert('反馈失败')
  }
}

onMounted(async () => {
  await loadCompanion()
  await loadPendingEvents()
  initWebSocket()
})

onBeforeUnmount(() => {
  removeAllListeners()
  disconnect()
  if (affinityTimeout) {
    clearTimeout(affinityTimeout)
  }
})
</script>

<template>
  <div class="h-screen flex bg-gradient-to-b from-pink-50 to-white">
    <!-- 主聊天区域 -->
    <div class="flex-1 flex flex-col">
      <!-- 顶部栏 -->
      <div class="bg-white border-b px-6 py-4 shadow-sm">
        <div class="max-w-4xl mx-auto flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <button
              @click="router.push({ name: 'home' })"
              class="text-gray-500 hover:text-gray-700"
            >
              ← 返回
            </button>
            <div v-if="companion" class="flex items-center space-x-3">
              <!-- 使用头像组件 -->
              <CompanionAvatar
                :companion-id="companion.personality_archetype || 'linzixi'"
                :companion-name="companion.name"
                :level-key="romanceLevel || 'stranger'"
                :affinity-score="affinityScore || 50"
                size="medium"
                :show-level-badge="true"
                :animated="true"
              />
              <div>
                <h2 class="font-bold text-gray-800">{{ companion.name }}</h2>
                <!-- 等级名称和描述 -->
                <div class="flex items-center space-x-2 text-xs">
                  <span
                    class="font-semibold"
                    :style="{ color: levelConfig?.color || '#6b7280' }"
                  >
                    {{ levelConfig?.name || '关系初始化中' }}
                  </span>
                  <span class="text-gray-400">·</span>
                  <span class="text-gray-500">好感度 {{ affinityScore ?? '--' }}</span>
                </div>
                <!-- 等级进度条 -->
                <div class="mt-1 w-48">
                  <div class="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      class="h-full transition-all duration-500 ease-out rounded-full"
                      :style="{
                        width: levelProgress + '%',
                        background: `linear-gradient(90deg, ${levelConfig?.color || '#6b7280'} 0%, ${levelConfig?.bgColor || '#e5e7eb'} 100%)`
                      }"
                    ></div>
                  </div>
                  <p class="text-xs text-gray-400 mt-0.5">{{ levelConfig?.description || '' }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <div class="relative flex items-center space-x-1 bg-pink-50 border border-pink-200 px-3 py-2 rounded-lg">
              <span class="text-lg">❤️</span>
              <span class="text-sm font-semibold text-pink-600">{{ affinityScore ?? '--' }}</span>
              <transition name="affinity-pop">
                <div
                  v-if="showAffinityChange"
                  class="absolute -top-6 left-1/2 -translate-x-1/2 flex items-center space-x-1 text-sm font-semibold"
                  :class="affinityDelta > 0 ? 'text-pink-500' : 'text-blue-500'"
                >
                  <span>{{ affinityDelta > 0 ? '+' : '' }}{{ affinityDelta }}</span>
                  <span>❤</span>
                </div>
              </transition>
            </div>
            <!-- 恋爱攻略面板切换按钮 -->
            <button
              @click="showRomancePanel = !showRomancePanel"
              :class="[
                'px-3 py-2 rounded-lg text-sm font-medium transition-all',
                showRomancePanel 
                  ? 'bg-pink-500 text-white' 
                  : 'bg-pink-100 text-pink-600 hover:bg-pink-200'
              ]"
            >
              💖 恋爱攻略
            </button>
            
            <!-- WebSocket连接状态 -->
            <div class="flex items-center space-x-1">
              <span 
                :class="[
                  'w-2 h-2 rounded-full',
                  isConnected ? 'bg-green-500' : isConnecting ? 'bg-yellow-500' : 'bg-red-500'
                ]"
              ></span>
              <span :class="[
                'text-xs',
                isConnected ? 'text-green-600' : isConnecting ? 'text-yellow-600' : 'text-red-600'
              ]">
                {{ isConnected ? '已连接' : isConnecting ? '连接中' : '已断开' }}
              </span>
            </div>
            
            <!-- 会话信息 -->
            <span v-if="currentChatSession" class="text-xs text-gray-500">
              {{ currentChatSession.session_title }}
            </span>
          </div>
        </div>
      </div>

      <!-- 聊天区域 -->
      <div
        ref="chatContainer"
        class="flex-1 overflow-y-auto px-6 py-6"
      >
        <div class="max-w-4xl mx-auto space-y-4">
          <!-- 事件卡片（置顶显示） -->
          <div v-if="currentEvent" class="mb-6">
            <EventCard
              :event="currentEvent"
              @interact="handleEventInteract"
              @close="closeEventCard"
            />
          </div>

          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="[
              'flex',
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <div
              :class="[
                'max-w-xs md:max-w-md px-4 py-3 rounded-2xl',
                msg.role === 'user'
                  ? 'bg-primary-500 text-white'
                  : 'bg-white border border-gray-200 text-gray-800'
              ]"
            >
              <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ msg.content }}</p>
              
            </div>
          </div>

          <!-- 加载中提示 -->
          <div v-if="isLoading" class="flex justify-start">
            <div class="bg-white border border-gray-200 px-4 py-3 rounded-2xl">
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="bg-white border-t px-6 py-4">
        <div class="max-w-4xl mx-auto">
          <form @submit.prevent="sendMessage" class="flex items-end space-x-3">
            <textarea
              v-model="userInput"
              @keydown.enter.exact.prevent="sendMessage"
              placeholder="说点什么吧..."
              rows="1"
              class="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:outline-none resize-none"
              :disabled="isLoading || !isConnected"
            ></textarea>
            <button
              type="submit"
              :disabled="!userInput.trim() || isLoading || !isConnected"
              class="px-6 py-3 bg-primary-500 text-white rounded-xl font-medium hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {{ isLoading ? '发送中...' : !isConnected ? '未连接' : '发送' }}
            </button>
          </form>
          <p class="text-xs text-gray-400 mt-2 text-center">
            按 Enter 发送, Shift + Enter 换行
          </p>
        </div>
      </div>
    </div>

    <!-- 恋爱攻略侧边栏 -->
    <div 
      v-if="showRomancePanel && companion"
      class="w-96 bg-white border-l border-gray-200 flex-shrink-0 overflow-y-auto"
    >
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-800">恋爱攻略</h3>
          <button
            @click="showRomancePanel = false"
            class="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
      </div>
      
      <div class="p-4">
        <RomancePanel
          ref="romancePanelRef"
          :companion-id="companionId"
          :companion-name="companion.name"
          :user-id="userStore.userId || 'default'"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.affinity-pop-enter-active {
  animation: heartFloat 1.2s ease-out forwards;
}

.affinity-pop-leave-active {
  animation: heartFloat 0.6s ease-in reverse forwards;
}

.affinity-pop-enter-from,
.affinity-pop-leave-to {
  opacity: 0;
}

@keyframes heartFloat {
  0% {
    opacity: 0;
    transform: translate(-50%, 0) scale(0.8);
  }
  20% {
    opacity: 1;
    transform: translate(-50%, -10px) scale(1);
  }
  80% {
    opacity: 1;
    transform: translate(-50%, -30px) scale(1.05);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -40px) scale(0.9);
  }
}
</style>
