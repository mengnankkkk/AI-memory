<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { companionService, chatService } from '@/services/companion'
import type { Companion, ChatMessage } from '@/types'

const route = useRoute()
const router = useRouter()

const companionId = Number(route.params.companionId)
const sessionId = ref(`session_${Date.now()}`)

const companion = ref<Companion | null>(null)
const messages = ref<ChatMessage[]>([])
const userInput = ref('')
const isLoading = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

// 加载伙伴信息
const loadCompanion = async () => {
  try {
    companion.value = await companionService.get(companionId)
    // 添加问候消息
    messages.value.push({
      role: 'assistant',
      content: companion.value.greeting
    })
  } catch (error) {
    console.error('加载失败:', error)
    alert('无法加载伙伴信息')
    router.push({ name: 'home' })
  }
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
  if (!userInput.value.trim() || isLoading.value) return

  const message = userInput.value.trim()
  userInput.value = ''

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message
  })
  scrollToBottom()

  isLoading.value = true
  try {
    const response = await chatService.sendMessage({
      companion_id: companionId,
      message: message,
      session_id: sessionId.value
    })

    // 添加助手回复
    messages.value.push({
      role: 'assistant',
      content: response.message
    })
    scrollToBottom()
  } catch (error) {
    console.error('发送失败:', error)
    alert('消息发送失败,请重试')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadCompanion()
})
</script>

<template>
  <div class="h-screen flex flex-col bg-gradient-to-b from-pink-50 to-white">
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
          <span class="text-xs text-green-500 flex items-center">
            <span class="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
            在线
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
            :disabled="isLoading"
          ></textarea>
          <button
            type="submit"
            :disabled="!userInput.trim() || isLoading"
            class="px-6 py-3 bg-primary-500 text-white rounded-xl font-medium hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            发送
          </button>
        </form>
        <p class="text-xs text-gray-400 mt-2 text-center">
          按 Enter 发送, Shift + Enter 换行
        </p>
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
