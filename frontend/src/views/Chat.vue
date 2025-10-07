<script setup lang="ts">
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { companionService } from '@/services/companion'
import { useUserStore } from '@/stores/user'
import { useWebSocketChat } from '@/services/websocket'
import RomancePanel from '@/components/RomancePanel.vue'
import type { Companion, ChatMessage } from '@/types'
import api from '@/services/auth'

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
  onMessageReceived,
  onResponseStart,
  onResponseChunk,
  onResponseEnd,
  onError,
  onChatJoined,
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
    
    // 加载聊天会话历史
    await loadChatHistory()
    
  } catch (error) {
    console.error('加载失败:', error)
    alert('无法加载伙伴信息')
    router.push({ name: 'home' })
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
  onResponseEnd((fullContent) => {
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
    // 通过WebSocket发送消息
    sendSocketMessage(message)
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
  initWebSocket()
})

onBeforeUnmount(() => {
  removeAllListeners()
  disconnect()
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
            <div v-if="companion" class="flex items-center space-x-2">
              <div class="text-3xl">{{ companion.avatar_id === 'avatar_01' ? '🌸' : '🌟' }}</div>
              <div>
                <h2 class="font-bold text-gray-800">{{ companion.name }}</h2>
                <p class="text-xs text-gray-500">
                  {{
                    companion.personality_archetype === 'listener' ? '温柔的倾听者' :
                    companion.personality_archetype === 'cheerleader' ? '元气的鼓励者' :
                    '理性的分析者'
                  }}
                </p>
              </div>
            </div>
          </div>

          <div class="flex items-center space-x-2">
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
              
              <!-- 点赞/点踩按钮 -->
              <div v-if="msg.role === 'assistant'" class="flex space-x-2 mt-2">
                <button
                  @click="feedback(msg, 1)"
                  class="flex items-center px-3 py-1 text-sm font-medium text-green-600 bg-green-100 rounded-lg hover:bg-green-200 transition-all"
                >
                  👍
                </button>
                <button
                  @click="feedback(msg, -1)"
                  class="flex items-center px-3 py-1 text-sm font-medium text-red-600 bg-red-100 rounded-lg hover:bg-red-200 transition-all"
                >
                  👎
                </button>
              </div>
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
</style>
