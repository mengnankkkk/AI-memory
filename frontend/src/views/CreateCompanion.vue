<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { companionService } from '@/services/companion'
import type { CompanionCreate } from '@/types'

const router = useRouter()

const step = ref(1)
const formData = ref<CompanionCreate>({
  user_id: 'demo_user', // 实际应用中从认证系统获取
  name: '',
  avatar_id: 'avatar_01',
  personality_archetype: 'listener'
})

const personalities = [
  {
    id: 'listener',
    name: '温柔的倾听者',
    description: 'TA会永远耐心地听你诉说,给你最温暖的鼓励和最治愈的安慰',
    emoji: '💖'
  },
  {
    id: 'cheerleader',
    name: '元气的鼓励者',
    description: 'TA像一颗小太阳,充满活力,总能发现生活中的美好,为你加油打气',
    emoji: '✨'
  },
  {
    id: 'analyst',
    name: '理性的分析者',
    description: 'TA博学而冷静,当你遇到难题时,TA会帮你分析问题,提供清晰的思路和逻辑建议',
    emoji: '🧠'
  }
]

const avatars = [
  { id: 'avatar_01', emoji: '🌸' },
  { id: 'avatar_02', emoji: '🌟' },
  { id: 'avatar_03', emoji: '🌙' },
  { id: 'avatar_04', emoji: '🍀' },
  { id: 'avatar_05', emoji: '🦋' },
  { id: 'avatar_06', emoji: '🌈' }
]

const isCreating = ref(false)

const nextStep = () => {
  if (step.value < 3) step.value++
}

const prevStep = () => {
  if (step.value > 1) step.value--
}

const createCompanion = async () => {
  if (!formData.value.name.trim()) {
    alert('请输入伙伴的名字')
    return
  }

  isCreating.value = true
  try {
    const companion = await companionService.create(formData.value)
    router.push({ name: 'chat', params: { companionId: companion.id } })
  } catch (error) {
    console.error('创建失败:', error)
    alert('创建失败,请重试')
  } finally {
    isCreating.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-8">
      <!-- 标题 -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">创建你的AI伙伴</h1>
        <p class="text-gray-500">让我们开始这段奇妙的旅程吧</p>
      </div>

      <!-- 进度条 -->
      <div class="flex justify-between mb-12">
        <div v-for="i in 3" :key="i" class="flex-1">
          <div class="flex items-center">
            <div
              :class="[
                'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold',
                step >= i ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-400'
              ]"
            >
              {{ i }}
            </div>
            <div v-if="i < 3" class="flex-1 h-1 mx-2" :class="step > i ? 'bg-primary-500' : 'bg-gray-200'"></div>
          </div>
        </div>
      </div>

      <!-- Step 1: 命名 -->
      <div v-if="step === 1" class="space-y-6">
        <div>
          <label class="block text-lg font-medium text-gray-700 mb-3">给TA起个名字吧</label>
          <input
            v-model="formData.name"
            type="text"
            placeholder="例如: 小可、Mia、晨曦..."
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:outline-none text-lg"
            maxlength="20"
          />
          <p class="mt-2 text-sm text-gray-500">这个名字将是TA的专属标识</p>
        </div>
      </div>

      <!-- Step 2: 形象选择 -->
      <div v-if="step === 2" class="space-y-6">
        <div>
          <label class="block text-lg font-medium text-gray-700 mb-4">选择TA的形象</label>
          <div class="grid grid-cols-3 gap-4">
            <div
              v-for="avatar in avatars"
              :key="avatar.id"
              @click="formData.avatar_id = avatar.id"
              :class="[
                'p-6 border-2 rounded-xl cursor-pointer transition-all hover:shadow-md',
                formData.avatar_id === avatar.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200'
              ]"
            >
              <div class="text-6xl text-center">{{ avatar.emoji }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: 性格原型 -->
      <div v-if="step === 3" class="space-y-4">
        <div>
          <label class="block text-lg font-medium text-gray-700 mb-4">选择TA的性格</label>
          <div class="space-y-3">
            <div
              v-for="personality in personalities"
              :key="personality.id"
              @click="formData.personality_archetype = personality.id"
              :class="[
                'p-4 border-2 rounded-xl cursor-pointer transition-all hover:shadow-md',
                formData.personality_archetype === personality.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200'
              ]"
            >
              <div class="flex items-start">
                <div class="text-3xl mr-3">{{ personality.emoji }}</div>
                <div class="flex-1">
                  <h3 class="font-bold text-gray-800 mb-1">{{ personality.name }}</h3>
                  <p class="text-sm text-gray-600">{{ personality.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex justify-between mt-8 pt-6 border-t">
        <button
          v-if="step > 1"
          @click="prevStep"
          class="px-6 py-2 text-gray-600 hover:text-gray-800 font-medium"
        >
          上一步
        </button>
        <div v-else></div>

        <button
          v-if="step < 3"
          @click="nextStep"
          :disabled="step === 1 && !formData.name.trim()"
          :class="[
            'px-8 py-3 rounded-lg font-medium transition-all',
            step === 1 && !formData.name.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-primary-500 text-white hover:bg-primary-600'
          ]"
        >
          下一步
        </button>

        <button
          v-else
          @click="createCompanion"
          :disabled="isCreating"
          class="px-8 py-3 bg-primary-500 text-white rounded-lg font-medium hover:bg-primary-600 disabled:opacity-50"
        >
          {{ isCreating ? '创建中...' : '完成创建' }}
        </button>
      </div>
    </div>
  </div>
</template>
