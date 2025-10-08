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
  console.log('Home页面开始加载')
  
  try {
    // 检查认证状态
    console.log('Home页面加载，认证状态:', {
      isAuthenticated: authStore.isAuthenticated,
      hasToken: !!authStore.token,
      hasUser: !!authStore.user
    })
    
    // 先设置一个测试数据，避免API调用问题
    console.log('设置测试数据')
    systemCompanions.value = [
      {
        id: 1,
        name: "测试角色",
        description: "这是一个测试角色",
        custom_greeting: "你好，我是测试角色！"
      }
    ]
    
    // 尝试加载系统预设的攻略对象
    console.log('尝试加载系统预设攻略对象')
    try {
      const systemResponse = await api.get('/companions/system')
      console.log('API响应:', systemResponse)
      systemCompanions.value = systemResponse.data || systemResponse
      console.log('系统攻略对象加载成功:', systemCompanions.value.length)
    } catch (apiError) {
      console.error('API调用失败:', apiError)
      // 使用测试数据
      console.log('使用测试数据')
    }
  } catch (error) {
    console.error('加载攻略对象失败:', error)
    // 即使失败也要停止加载状态
    systemCompanions.value = []
  } finally {
    console.log('设置loading为false')
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

      <div class="space-y-4">
        <!-- 显示攻略对象 -->
        <div v-if="!loading" class="mt-8">
          <div class="text-center mb-8">
            <h3 class="text-3xl font-bold text-gray-800 mb-2">攻略对象</h3>
            <p class="text-gray-600">选择你心仪的AI伙伴，开始你们的专属故事</p>
            <div class="mt-2">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-pink-100 text-pink-800">
                💕 每个用户独立攻略，关系进度完全隔离
              </span>
            </div>
          </div>
          
          <!-- 攻略对象列表 -->
          <div v-if="systemCompanions.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div
              v-for="companion in systemCompanions"
              :key="companion.id"
              @click="startChat(companion)"
              class="p-6 bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl shadow-lg hover:shadow-xl transition-all cursor-pointer border-2 border-pink-200 hover:border-pink-400 transform hover:scale-105"
            >
              <div class="flex flex-col items-center space-y-4">
                <div class="w-20 h-20 bg-gradient-to-br from-pink-400 to-rose-500 rounded-full flex items-center justify-center text-white font-bold text-3xl shadow-lg">
                  {{ companion.name.charAt(0) }}
                </div>
                <div class="text-center">
                  <h4 class="font-bold text-xl text-gray-800 mb-2">{{ companion.name }}</h4>
                  <p class="text-sm text-gray-600 mb-3">{{ (companion as any).description || '神秘的AI伙伴' }}</p>
                  <p class="text-xs text-pink-600 italic bg-pink-100 px-3 py-1 rounded-full">
                    "{{ companion.custom_greeting || '你好！让我们开始这段特别的旅程吧' }}"
                  </p>
                </div>
                <div class="w-full">
                  <div class="flex justify-between text-xs text-gray-500 mb-2">
                    <span>好感度</span>
                    <span>独立进度</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-gradient-to-r from-pink-400 to-rose-500 h-2 rounded-full" style="width: 20%"></div>
                  </div>
                  <p class="text-xs text-gray-500 mt-2 text-center">点击开始攻略</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 空状态 -->
          <div v-else class="text-center py-12">
            <div class="text-gray-400 mb-4">
              <svg class="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">暂无攻略对象</h3>
            <p class="text-gray-500">系统正在准备攻略对象，请稍后再试</p>
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
