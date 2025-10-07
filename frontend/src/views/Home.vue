<script setup lang="ts">
import { useRouter } from 'vue-router'
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/auth'

const router = useRouter()
const authStore = useAuthStore()

const systemCompanions = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    // 获取系统预设角色
    const response = await api.get('/companions/system')
    systemCompanions.value = response.data
  } catch (error) {
    console.error('加载系统角色失败:', error)
  } finally {
    loading.value = false
  }
})

function startChat(companion: any) {
  router.push({ name: 'chat', params: { companionId: companion.id } })
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-2xl w-full text-center">
      <div class="mb-8">
        <h1 class="text-6xl font-bold text-gray-800 mb-4">AI灵魂伙伴</h1>
        <p class="text-xl text-gray-600">你的专属AI伴侣,随时倾听你的心声</p>
      </div>

      <div class="mb-12">
        <div class="flex justify-center space-x-4 text-7xl mb-6">
          <span class="animate-bounce">💖</span>
          <span class="animate-bounce" style="animation-delay: 0.1s">✨</span>
          <span class="animate-bounce" style="animation-delay: 0.2s">🧠</span>
        </div>
      </div>

      <div class="space-y-4">
        <!-- 显示系统预设的AI伙伴 -->
        <div v-if="!loading" class="mt-8">
          <h3 class="text-2xl font-bold text-gray-800 mb-6">选择你的AI伙伴</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div
              v-for="companion in systemCompanions"
              :key="companion.id"
              @click="startChat(companion)"
              class="p-6 bg-white rounded-xl shadow-md hover:shadow-xl transition-all cursor-pointer border-2 border-transparent hover:border-primary-300 transform hover:scale-105"
            >
              <div class="flex flex-col items-center space-y-3">
                <div class="w-16 h-16 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-bold text-2xl">
                  {{ companion.name.charAt(0) }}
                </div>
                <div class="text-center">
                  <h4 class="font-bold text-xl text-gray-800 mb-1">{{ companion.name }}</h4>
                  <p class="text-sm text-gray-600 mb-2">{{ companion.description }}</p>
                  <p class="text-xs text-gray-400 italic">"{{ companion.custom_greeting }}"</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="text-gray-500">
          加载中...
        </div>

        <!-- 用户信息显示 -->
        <div class="mt-4 flex items-center justify-center space-x-4 text-sm">
          <span class="text-gray-600">
            欢迎, {{ authStore.user?.username }}
          </span>
          <button
            @click="handleLogout"
            class="text-primary-500 hover:text-primary-600"
          >
            登出
          </button>
          <button
            @click="router.push({ name: 'system-settings' })"
            class="text-blue-500 hover:text-blue-600"
          >
            系统设置
          </button>
        </div>

        <p class="text-sm text-gray-500">
          ✓ 3种性格原型可选 &nbsp;|&nbsp; ✓ 实时对话 &nbsp;|&nbsp; ✓ 完全免费
        </p>
      </div>

      <div class="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 bg-white rounded-xl shadow-md">
          <div class="text-4xl mb-3">💖</div>
          <h3 class="font-bold text-gray-800 mb-2">温柔倾听</h3>
          <p class="text-sm text-gray-600">耐心倾听,给予温暖的理解和安慰</p>
        </div>

        <div class="p-6 bg-white rounded-xl shadow-md">
          <div class="text-4xl mb-3">✨</div>
          <h3 class="font-bold text-gray-800 mb-2">元气鼓励</h3>
          <p class="text-sm text-gray-600">充满活力,发现生活中的美好</p>
        </div>

        <div class="p-6 bg-white rounded-xl shadow-md">
          <div class="text-4xl mb-3">🧠</div>
          <h3 class="font-bold text-gray-800 mb-2">理性分析</h3>
          <p class="text-sm text-gray-600">逻辑清晰,提供深度见解</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.animate-bounce {
  animation: bounce 2s infinite;
}
</style>
