<script setup lang="ts">
import { ref } from 'vue'

interface EventDialogue {
  speaker: string
  text: string
}

interface EventScriptContent {
  title: string
  description: string
  image?: string
  dialogue: EventDialogue[]
}

interface EventData {
  event_id: number
  event_name: string
  event_type: string
  category: string
  script_content: EventScriptContent
  image_url?: string
  history_id: number
  companion_name?: string
}

const props = defineProps<{
  event: EventData
}>()

const emit = defineEmits<{
  interact: [historyId: number]
  close: []
}>()

const showDetails = ref(false)

function handleInteract() {
  emit('interact', props.event.history_id)
}

function replaceNames(text: string): string {
  return text.replace(/\{name\}/g, props.event.companion_name || '伙伴')
}
</script>

<template>
  <div class="event-card bg-gradient-to-br from-pink-50 to-purple-50 rounded-2xl shadow-lg p-6 border-2 border-pink-200">
    <!-- 事件标题 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3">
        <span class="text-3xl">✨</span>
        <div>
          <h3 class="text-xl font-bold text-gray-800">{{ event.script_content.title }}</h3>
          <p class="text-sm text-gray-500">{{ event.event_name }}</p>
        </div>
      </div>
      <button
        @click="$emit('close')"
        class="text-gray-400 hover:text-gray-600 transition"
      >
        ✕
      </button>
    </div>

    <!-- 事件图片 -->
    <div
      v-if="event.image_url"
      class="relative rounded-xl overflow-hidden mb-4 shadow-md"
    >
      <img
        :src="event.image_url"
        :alt="event.event_name"
        class="w-full h-64 object-cover"
        @error="($event.target as HTMLImageElement).style.display='none'"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent"></div>
    </div>

    <!-- 事件描述 -->
    <p class="text-gray-700 mb-4 leading-relaxed">
      {{ replaceNames(event.script_content.description) }}
    </p>

    <!-- 对话内容 -->
    <div v-if="!showDetails" class="mb-4">
      <button
        @click="showDetails = true"
        class="text-pink-500 hover:text-pink-600 text-sm font-medium"
      >
        查看详情 →
      </button>
    </div>

    <div v-else class="space-y-3 mb-4">
      <div
        v-for="(line, index) in event.script_content.dialogue"
        :key="index"
        :class="[
          'p-3 rounded-lg',
          line.speaker === 'system' ? 'bg-gray-100 text-gray-600 italic' : 'bg-white text-gray-800'
        ]"
      >
        <p class="text-sm">
          {{ replaceNames(line.text) }}
        </p>
      </div>
    </div>

    <!-- 交互按钮 -->
    <div class="flex space-x-3">
      <button
        @click="handleInteract"
        class="flex-1 bg-gradient-to-r from-pink-500 to-purple-500 text-white py-3 rounded-xl font-medium hover:shadow-lg transition-all"
      >
        💬 和TA聊聊这个
      </button>
      <button
        @click="$emit('close')"
        class="px-6 py-3 bg-gray-100 text-gray-600 rounded-xl font-medium hover:bg-gray-200 transition"
      >
        稍后
      </button>
    </div>
  </div>
</template>

<style scoped>
.event-card {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
