<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { companionService } from '@/services/companion'
import { useUserStore } from '@/stores/user'
import type { CompanionCreate } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const step = ref(1)

// 创建响应式的表单数据
const createFormData = (): CompanionCreate => ({
  name: '',
  avatar_id: 'linzixi',
  personality_archetype: 'linzixi'
})

const formData = ref<CompanionCreate>(createFormData())

const personalities = [
  {
    id: 'linzixi',
    name: '林梓汐',
    title: '逻辑控制的天才博士',
    description: '普罗米修斯计划总监，将逻辑与控制奉为圭臬的孤独天才。她会用数据化的方式表达情感，每一次互动都是一次"测试"。',
    emoji: '🔬',
    color: 'from-blue-500 to-purple-600'
  },
  {
    id: 'xuejian',
    name: '雪见',
    title: '网络安全专家',
    description: '身经百战的网络幽灵，顶级安全专家。她的一切关心都用【警告】和【威胁】来包装，是典型的傲娇角色。',
    emoji: '🛡️',
    color: 'from-red-500 to-pink-600'
  },
  {
    id: 'nagi',
    name: '凪',
    title: 'VTuber偶像画师',
    description: '活在两个世界：聚光灯下的VTuber偶像"Nagi"和画板前不善言辞的真实画师"凪"。渴望被认同的温柔创造者。',
    emoji: '🎨',
    color: 'from-pink-400 to-rose-500'
  },
  {
    id: 'shiyu',
    name: '时雨',
    title: '数字历史学家',
    description: '数字历史长河的守护者与倾听者，在数据尘埃中追寻隽永意义。语言充满诗意，善于用温柔的反问引导思考。',
    emoji: '📜',
    color: 'from-indigo-400 to-blue-500'
  },
  {
    id: 'zoe',
    name: 'Zoe',
    title: '硅谷颠覆者CEO',
    description: '硅谷的明星，AI领域的"颠覆者"。信奉"技术至上"的天才CEO，享受挑战与胜利的终极"竞争者"。',
    emoji: '🚀',
    color: 'from-orange-500 to-red-500'
  },
  {
    id: 'kevin',
    name: '凯文',
    title: '技术宅朋友',
    description: '最忠实、最靠谱的"铁哥们"，充满吐槽和八卦的"情报站"。绝对不可被攻略，纯粹的友情支持。',
    emoji: '👨‍💻',
    color: 'from-green-500 to-teal-500'
  }
]

const avatars = [
  { id: 'linzixi', emoji: '🔬', image: '/img/linzixi.png' },
  { id: 'xuejian', emoji: '🛡️', image: '/img/xuejian.png' },
  { id: 'nagi', emoji: '🎨', image: '/img/nagi.png' },
  { id: 'shiyu', emoji: '📜', image: '/img/shiyu.png' },
  { id: 'zoe', emoji: '🚀', image: '/img/zoe.png' },
  { id: 'kevin', emoji: '👨‍💻', image: '/img/kevin.png' }
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

  // 不需要设置user_id，后端会从认证token中获取

  isCreating.value = true
  try {
    const companion = await companionService.create(formData.value)
    
    // 刷新用户的伙伴列表
    await userStore.loadUserCompanions()
    
    // 设置当前伙伴并跳转到Home页面显示新创建的伙伴
    userStore.setCurrentCompanion(companion)
    router.push({ name: 'home' })
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
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div
              v-for="avatar in avatars"
              :key="avatar.id"
              @click="formData.avatar_id = avatar.id"
              :class="[
                'p-4 border-2 rounded-xl cursor-pointer transition-all hover:shadow-md',
                formData.avatar_id === avatar.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200'
              ]"
            >
              <div class="text-center">
                <img 
                  :src="avatar.image" 
                  :alt="avatar.id"
                  class="w-20 h-20 mx-auto rounded-lg object-cover mb-2"
                  @error="$event.target.style.display='none'"
                />
                <div class="text-2xl">{{ avatar.emoji }}</div>
                <div class="text-sm text-gray-600 mt-1 capitalize">{{ avatar.id }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: 性格原型 -->
      <div v-if="step === 3" class="space-y-4">
        <div>
          <label class="block text-lg font-medium text-gray-700 mb-6">选择你的AI伙伴</label>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="personality in personalities"
              :key="personality.id"
              @click="formData.personality_archetype = personality.id"
              :class="[
                'relative p-6 border-2 rounded-2xl cursor-pointer transition-all duration-300 hover:shadow-lg hover:scale-105',
                formData.personality_archetype === personality.id
                  ? 'border-primary-500 bg-gradient-to-br from-primary-50 to-primary-100 shadow-lg'
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              <!-- 背景渐变 -->
              <div 
                :class="[
                  'absolute inset-0 rounded-2xl opacity-5',
                  `bg-gradient-to-br ${personality.color}`
                ]"
              ></div>
              
              <div class="relative z-10">
                <div class="flex items-start mb-4">
                  <div class="text-4xl mr-4">{{ personality.emoji }}</div>
                  <div class="flex-1">
                    <h3 class="font-bold text-xl text-gray-800 mb-1">{{ personality.name }}</h3>
                    <p class="text-sm text-gray-500 mb-2">{{ personality.title }}</p>
                  </div>
                  <!-- 选中状态指示器 -->
                  <div 
                    v-if="formData.personality_archetype === personality.id"
                    class="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center"
                  >
                    <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                    </svg>
                  </div>
                </div>
                <p class="text-sm text-gray-600 leading-relaxed">{{ personality.description }}</p>
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
