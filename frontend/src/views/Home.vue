<script setup lang="ts">
import { useRouter } from 'vue-router'
import { onMounted, ref, computed, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/auth'
import { romanceApi } from '@/services/romance'
import CompanionAvatar from '@/components/CompanionAvatar.vue'
import LevelUpModal from '@/components/LevelUpModal.vue'
import { getLevelConfig, getLevelByScore, getLevelProgress } from '@/config/affinity-config'
import type { CompanionStateResponse } from '@/types/romance'

const router = useRouter()
const authStore = useAuthStore()

const systemCompanions = ref<any[]>([])
const companionStates = reactive<Record<number, CompanionStateResponse>>({})
const loading = ref(true)
const loadingStates = ref(true)

// 升级庆祝弹窗
const showLevelUpModal = ref(false)
const levelUpData = ref<{
  levelKey: string
  affinityScore: number
  companionName: string
  message: string
} | null>(null)

onMounted(async () => {
  console.log('Home页面开始加载')

  try {
    // 检查认证状态
    console.log('Home页面加载，认证状态:', {
      isAuthenticated: authStore.isAuthenticated,
      hasToken: !!authStore.token,
      hasUser: !!authStore.user,
      userId: authStore.user?.id
    })

    // 加载系统预设的攻略对象
    console.log('加载系统预设攻略对象')
    try {
      const systemResponse = await api.get('/companions/system')
      console.log('API响应:', systemResponse)
      systemCompanions.value = systemResponse.data || systemResponse
      console.log('系统攻略对象加载成功:', systemCompanions.value.length)

      // 加载每个角色的好感度状态
      await loadCompanionStates()
    } catch (apiError) {
      console.error('API调用失败:', apiError)
      systemCompanions.value = []
    }
  } catch (error) {
    console.error('加载攻略对象失败:', error)
    systemCompanions.value = []
  } finally {
    console.log('设置loading为false')
    loading.value = false
  }
})

// 加载所有角色的好感度状态
const loadCompanionStates = async () => {
  loadingStates.value = true
  const userId = authStore.user?.id?.toString() || 'default'

  for (const key of Object.keys(companionStates)) {
    delete companionStates[Number(key)]
  }

  for (const companion of systemCompanions.value) {
    try {
      const state = await romanceApi.getCompanionState(companion.id, userId)
      companionStates[companion.id] = state
      console.log(`角色 ${companion.name} 状态:`, state)
    } catch (error) {
      console.error(`加载角色${companion.id}状态失败:`, error)
      // 使用默认状态
      companionStates[companion.id] = {
        affinity_score: 50,
        trust_score: 10,
        tension_score: 0,
        romance_level: 'stranger',
        current_mood: '平静',
        mood_last_updated: Math.floor(Date.now() / 1000),
        last_interaction_at: Math.floor(Date.now() / 1000),
        total_interactions: 0,
        days_since_first_meet: 0,
        special_events_triggered: [],
        gifts_received: [],
        outfit_unlocked: [],
        memories: []
      }
    }
  }

  loadingStates.value = false
}

// 获取角色状态
const getCompanionState = (companionId: number): CompanionStateResponse => {
  if (companionStates[companionId]) {
    return companionStates[companionId]
  }

  const fallbackTimestamp = Math.floor(Date.now() / 1000)
  return {
    affinity_score: 50,
    trust_score: 10,
    tension_score: 0,
    romance_level: 'stranger',
    current_mood: '平静',
    mood_last_updated: fallbackTimestamp,
    last_interaction_at: fallbackTimestamp,
    total_interactions: 0,
    days_since_first_meet: 0,
    special_events_triggered: [],
    gifts_received: [],
    outfit_unlocked: [],
    memories: []
  }
}

// 获取等级信息
const getLevelInfo = (companionId: number) => {
  const state = getCompanionState(companionId)
  const levelConfig = getLevelConfig(state.romance_level)
  const progress = getLevelProgress(state.affinity_score, state.romance_level)
  return { levelConfig, progress, state }
}

function startChat(companion: any) {
  router.push({ name: 'chat', params: { companionId: companion.id } })
}

// 模拟升级（用于演示）
function simulateLevelUp(companion: any) {
  const state = getCompanionState(companion.id)
  const levelConfig = getLevelConfig(state.romance_level)

  levelUpData.value = {
    levelKey: state.romance_level,
    affinityScore: state.affinity_score,
    companionName: companion.name,
    message: `我们的关系进展到了${levelConfig.name}阶段！这让我感到很开心~`
  }
  showLevelUpModal.value = true
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
              class="companion-card p-6 bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl shadow-lg hover:shadow-2xl transition-all cursor-pointer border-2 border-pink-200 hover:border-pink-400 transform hover:scale-105 relative overflow-hidden"
            >
              <!-- 背景光晕效果 -->
              <div
                class="absolute inset-0 opacity-10 blur-3xl"
                :style="{ background: getLevelInfo(companion.id).levelConfig.color }"
              ></div>

              <div class="relative z-10 flex flex-col items-center space-y-4">
                <!-- 使用头像组件 -->
                <CompanionAvatar
                  :companion-id="companion.personality_archetype || 'linzixi'"
                  :companion-name="companion.name"
                  :level-key="getCompanionState(companion.id).romance_level"
                  :affinity-score="getCompanionState(companion.id).affinity_score"
                  size="large"
                  :show-level-badge="true"
                  :show-progress="false"
                  :animated="true"
                />

                <!-- 角色信息 -->
                <div class="text-center w-full">
                  <h4 class="font-bold text-xl text-gray-800 mb-1">{{ companion.name }}</h4>

                  <!-- 等级标签 -->
                  <div class="flex items-center justify-center space-x-2 mb-2">
                    <span
                      class="text-sm font-semibold px-3 py-1 rounded-full"
                      :style="{
                        background: getLevelInfo(companion.id).levelConfig.bgColor,
                        color: getLevelInfo(companion.id).levelConfig.color
                      }"
                    >
                      {{ getLevelInfo(companion.id).levelConfig.icon }} {{ getLevelInfo(companion.id).levelConfig.name }}
                    </span>
                  </div>

                  <p class="text-sm text-gray-600 mb-3">{{ (companion as any).description || '神秘的AI伙伴' }}</p>

                  <!-- 关系统计 -->
                  <div class="grid grid-cols-3 gap-2 mb-3 text-xs">
                    <div class="bg-white bg-opacity-60 rounded-lg p-2">
                      <div class="text-gray-500">交流</div>
                      <div class="font-bold text-gray-800">{{ getCompanionState(companion.id).total_interactions }}次</div>
                    </div>
                    <div class="bg-white bg-opacity-60 rounded-lg p-2">
                      <div class="text-gray-500">相识</div>
                      <div class="font-bold text-gray-800">{{ getCompanionState(companion.id).days_since_first_meet }}天</div>
                    </div>
                    <div class="bg-white bg-opacity-60 rounded-lg p-2">
                      <div class="text-gray-500">信任</div>
                      <div class="font-bold text-gray-800">{{ getCompanionState(companion.id).trust_score }}%</div>
                    </div>
                  </div>

                  <!-- 问候语 -->
                  <p class="text-xs text-pink-600 italic bg-pink-100 bg-opacity-80 px-3 py-2 rounded-full mb-3">
                    "{{ companion.custom_greeting || '你好！让我们开始这段特别的旅程吧' }}"
                  </p>
                </div>

                <!-- 好感度进度 -->
                <div class="w-full">
                  <div class="flex justify-between text-xs text-gray-600 mb-2">
                    <span>好感度</span>
                    <span class="font-semibold">{{ getCompanionState(companion.id).affinity_score }}/1000</span>
                  </div>

                  <!-- 进度条 -->
                  <div class="relative w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
                    <!-- 进度填充 -->
                    <div
                      class="absolute top-0 left-0 h-full rounded-full transition-all duration-700 ease-out progress-bar"
                      :style="{
                        width: (getCompanionState(companion.id).affinity_score / 1000 * 100) + '%',
                        background: `linear-gradient(90deg, ${getLevelInfo(companion.id).levelConfig.color} 0%, ${getLevelInfo(companion.id).levelConfig.bgColor} 100%)`
                      }"
                    >
                      <!-- 光泽效果 -->
                      <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-shimmer"></div>

                      <!-- 粒子效果 -->
                      <div class="particles-container">
                        <span v-for="i in 5" :key="i"
                          class="particle"
                          :style="{
                            left: (i * 20) + '%',
                            animationDelay: (i * 0.2) + 's',
                            background: getLevelInfo(companion.id).levelConfig.color
                          }"
                        ></span>
                      </div>
                    </div>

                    <!-- 当前等级进度 -->
                    <div class="absolute inset-0 flex items-center justify-center">
                      <span class="text-xs font-bold text-white mix-blend-difference drop-shadow-md">
                        等级进度 {{ Math.round(getLevelInfo(companion.id).progress) }}%
                      </span>
                    </div>
                  </div>

                  <p class="text-xs text-gray-500 mt-2 text-center">点击开始攻略</p>

                  <!-- 预览升级效果按钮 -->
                  <button
                    @click.stop="simulateLevelUp(companion)"
                    class="mt-3 w-full py-2 px-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-105 shadow-md"
                  >
                    ✨ 预览升级效果
                  </button>
                </div>
              </div>

              <!-- 悬浮效果闪光 -->
              <div class="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20 transform -skew-x-12 animate-slide"></div>
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

    <!-- 升级庆祝弹窗 -->
    <LevelUpModal
      v-if="levelUpData"
      :show="showLevelUpModal"
      :level-key="levelUpData.levelKey"
      :level-config="getLevelConfig(levelUpData.levelKey)"
      :affinity-score="levelUpData.affinityScore"
      :companion-name="levelUpData.companionName"
      :message="levelUpData.message"
      @close="showLevelUpModal = false"
    />
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

/* 进度条光泽动画 */
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}

/* 粒子效果 */
.particles-container {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  opacity: 0;
  animation: particleFloat 2s ease-in-out infinite;
}

@keyframes particleFloat {
  0% {
    transform: translateY(0) scale(0);
    opacity: 0;
  }
  50% {
    opacity: 0.8;
    transform: translateY(-10px) scale(1);
  }
  100% {
    transform: translateY(-20px) scale(0);
    opacity: 0;
  }
}

/* 进度条脉冲效果 */
.progress-bar {
  position: relative;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6));
  animation: progressPulse 1.5s ease-in-out infinite;
}

@keyframes progressPulse {
  0%, 100% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
}

/* 卡片悬浮闪光 */
@keyframes slide {
  0% {
    transform: translateX(-100%) skewX(-12deg);
  }
  100% {
    transform: translateX(100%) skewX(-12deg);
  }
}

.animate-slide {
  animation: slide 0.6s ease-out;
}

/* 卡片样式优化 */
.companion-card {
  position: relative;
  backdrop-filter: blur(10px);
}

.companion-card:hover {
  animation: cardPulse 0.3s ease-in-out;
}

@keyframes cardPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

/* 等级升级庆祝动画 */
@keyframes levelUpCelebration {
  0% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  50% {
    transform: scale(1.2) rotate(180deg);
    opacity: 0.8;
  }
  100% {
    transform: scale(1) rotate(360deg);
    opacity: 1;
  }
}

.level-up-celebration {
  animation: levelUpCelebration 0.8s ease-in-out;
}

/* 星星闪烁效果（为升级庆祝准备） */
@keyframes starTwinkle {
  0%, 100% {
    opacity: 0;
    transform: scale(0) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: scale(1) rotate(180deg);
  }
}

.star-effect {
  position: absolute;
  font-size: 20px;
  animation: starTwinkle 1s ease-out forwards;
  pointer-events: none;
}
</style>
