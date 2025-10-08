<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">系统设置</h1>
        <p class="mt-2 text-gray-600">管理系统配置、监控性能指标和查看使用统计</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p class="mt-4 text-gray-600">加载系统数据中...</p>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error && !loading" class="mb-6 bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-yellow-800">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- 主要内容 -->
      <div v-if="!loading">

      <!-- 统计概览卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span class="text-white font-semibold text-sm">会</span>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm text-gray-500">今日会话</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.today.sessions_created || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                <span class="text-white font-semibold text-sm">消</span>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm text-gray-500">处理消息</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.today.messages_processed || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                <span class="text-white font-semibold text-sm">缓</span>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm text-gray-500">缓存命中率</p>
              <p class="text-2xl font-semibold text-gray-900">{{ performance.cache_hit_rate || 0 }}%</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                <span class="text-white font-semibold text-sm">成</span>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm text-gray-500">成功率</p>
              <p class="text-2xl font-semibold text-gray-900">{{ performance.success_rate || 0 }}%</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 选项卡导航 -->
      <div class="border-b border-gray-200 mb-6">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- 攻略对象管理 -->
      <div v-if="activeTab === 'companions'" class="bg-white rounded-lg shadow">
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">攻略对象管理</h3>
              <p class="text-sm text-gray-500 mt-1">所有用户都可以攻略这些AI伙伴，但每个用户的关系进度是独立的</p>
            </div>
            <button
              @click="loadCompanions"
              :disabled="companionsLoading"
              class="px-4 py-2 bg-pink-500 text-white rounded-md hover:bg-pink-600 disabled:opacity-50"
            >
              {{ companionsLoading ? '加载中...' : '刷新' }}
            </button>
          </div>

          <!-- 攻略对象列表 -->
          <div v-if="systemCompanions.length > 0">
            <div class="mb-4 flex items-center justify-between">
              <h4 class="text-md font-medium text-gray-700">可攻略的AI伙伴 ({{ systemCompanions.length }})</h4>
              <div class="text-sm text-gray-500">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-pink-100 text-pink-800">
                  💕 每个用户独立攻略
                </span>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div
                v-for="companion in systemCompanions"
                :key="companion.id"
                @click="startChat(companion)"
                class="p-6 border-2 border-pink-200 rounded-xl hover:shadow-lg transition-all cursor-pointer hover:border-pink-400 hover:scale-105 bg-gradient-to-br from-pink-50 to-rose-50"
              >
                <div class="flex flex-col items-center space-y-4">
                  <div class="w-16 h-16 bg-gradient-to-br from-pink-400 to-rose-500 rounded-full flex items-center justify-center text-white font-bold text-2xl shadow-lg">
                    {{ companion.name.charAt(0) }}
                  </div>
                  <div class="text-center">
                    <h5 class="font-bold text-lg text-gray-900 mb-2">{{ companion.name }}</h5>
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
                    <p class="text-xs text-gray-500 mt-1 text-center">点击开始攻略</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="!companionsLoading && systemCompanions.length === 0" class="text-center py-12">
            <div class="text-gray-400 mb-4">
              <svg class="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">暂无攻略对象</h3>
            <p class="text-gray-500">系统正在准备攻略对象，请稍后再试</p>
          </div>
        </div>
      </div>

      <!-- 配置管理 -->
      <div v-if="activeTab === 'config'" class="bg-white rounded-lg shadow">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900">系统配置</h3>
            <button
              @click="showAddConfig = true"
              class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
            >
              添加配置
            </button>
          </div>

          <div class="space-y-4">
            <div
              v-for="(value, key) in configs"
              :key="key"
              class="flex items-center justify-between p-4 border rounded-lg"
            >
              <div>
                <h4 class="font-medium">{{ key }}</h4>
                <p class="text-sm text-gray-500">{{ typeof value === 'object' ? JSON.stringify(value) : value }}</p>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="editConfig(key, value)"
                  class="text-blue-500 hover:text-blue-700"
                >
                  编辑
                </button>
                <button
                  @click="deleteConfig(key)"
                  class="text-red-500 hover:text-red-700"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- A/B 测试管理 -->
      <div v-if="activeTab === 'ab-test'" class="bg-white rounded-lg shadow">
        <div class="p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">A/B 测试管理</h3>
          
          <div class="mb-6">
            <h4 class="font-medium mb-2">可用 Prompt 版本</h4>
            <div class="flex space-x-4">
              <span
                v-for="version in promptVersions.versions"
                :key="version"
                class="px-3 py-1 bg-gray-100 rounded-full text-sm"
              >
                {{ version }}
              </span>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-medium mb-2">Prompt 使用统计</h4>
              <div class="space-y-2">
                <div
                  v-for="(count, date) in promptUsageStats.prompt_usage"
                  :key="date"
                  class="flex justify-between"
                >
                  <span class="text-sm text-gray-600">{{ date }}</span>
                  <span class="text-sm font-medium">{{ count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据导出 -->
      <div v-if="activeTab === 'export'" class="bg-white rounded-lg shadow">
        <div class="p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">数据导出</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="border rounded-lg p-4">
              <h4 class="font-medium mb-2">对话记录导出</h4>
              <p class="text-sm text-gray-600 mb-4">导出用户对话记录为 CSV 格式</p>
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">用户ID（可选）</label>
                  <input
                    v-model="exportForm.userId"
                    type="number"
                    class="w-full border rounded-md px-3 py-2"
                    placeholder="留空导出所有用户"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">开始日期</label>
                  <input
                    v-model="exportForm.startDate"
                    type="date"
                    class="w-full border rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">结束日期</label>
                  <input
                    v-model="exportForm.endDate"
                    type="date"
                    class="w-full border rounded-md px-3 py-2"
                  />
                </div>
                <button
                  @click="exportConversations"
                  :disabled="exporting"
                  class="w-full bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50"
                >
                  {{ exporting ? '导出中...' : '导出对话记录' }}
                </button>
              </div>
            </div>

            <div class="border rounded-lg p-4">
              <h4 class="font-medium mb-2">系统统计导出</h4>
              <p class="text-sm text-gray-600 mb-4">导出系统使用统计和性能数据</p>
              <button
                @click="exportStats"
                class="w-full bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600"
              >
                导出统计数据
              </button>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>

    <!-- 添加/编辑配置弹窗 -->
    <div v-if="showAddConfig || editingConfig" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">{{ editingConfig ? '编辑配置' : '添加配置' }}</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">配置键</label>
            <input
              v-model="configForm.key"
              :disabled="editingConfig"
              type="text"
              class="w-full border rounded-md px-3 py-2"
              placeholder="例如: cache_ttl"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">配置值</label>
            <textarea
              v-model="configForm.value"
              class="w-full border rounded-md px-3 py-2"
              rows="3"
              placeholder="支持 JSON 格式"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">过期时间（秒）</label>
            <input
              v-model="configForm.ttl"
              type="number"
              class="w-full border rounded-md px-3 py-2"
              placeholder="留空使用默认值"
            />
          </div>
        </div>

        <div class="flex justify-end space-x-3 mt-6">
          <button
            @click="cancelConfigEdit"
            class="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            取消
          </button>
          <button
            @click="saveConfig"
            class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { configService, type StatsOverview, type PerformanceStats } from '@/services/config'
import api from '@/services/auth'

// 响应式数据
const activeTab = ref('companions')
const loading = ref(true)
const error = ref('')
const stats = ref<StatsOverview>({ today: {}, trends: {} })
const performance = ref<PerformanceStats>({
  cache_hit_rate: 0,
  success_rate: 0,
  total_requests: 0,
  cache_hits: 0,
  successful_responses: 0,
  error_responses: 0
})
const configs = ref<Record<string, any>>({})
const promptVersions = ref<{ versions: string[], current_default: string }>({ versions: [], current_default: '' })
const promptUsageStats = ref<{ prompt_usage: Record<string, number>, total_usage: number }>({ prompt_usage: {}, total_usage: 0 })

// 攻略对象管理相关
const systemCompanions = ref<any[]>([])
const companionsLoading = ref(false)

// 表单数据
const showAddConfig = ref(false)
const editingConfig = ref(false)
const configForm = ref({
  key: '',
  value: '',
  ttl: null as number | null
})

const exportForm = ref({
  userId: null as number | null,
  startDate: '',
  endDate: ''
})

const exporting = ref(false)

// 选项卡配置
const tabs = [
  { id: 'companions', name: '攻略对象' },
  { id: 'config', name: '配置管理' },
  { id: 'ab-test', name: 'A/B 测试' },
  { id: 'export', name: '数据导出' }
]

// 方法
const loadData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    console.log('开始加载系统数据...')
    
    // 设置超时时间
    const timeout = 10000 // 10秒超时
    
    // 加载统计数据
    const [statsData, performanceData, configsData, versionsData, usageData] = await Promise.all([
      Promise.race([
        configService.getStatsOverview(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('超时')), timeout))
      ]).catch((err) => {
        console.warn('获取统计数据失败:', err)
        return {
          today: {
            sessions_created: 0,
            messages_processed: 0,
            successful_responses: 0,
            error_responses: 0,
            cache_hits: 0,
            chat_sessions_joined: 0
          },
          trends: {}
        }
      }),
      Promise.race([
        configService.getPerformanceStats(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('超时')), timeout))
      ]).catch((err) => {
        console.warn('获取性能数据失败:', err)
        return {
          cache_hit_rate: 0,
          success_rate: 0,
          total_requests: 0,
          cache_hits: 0,
          successful_responses: 0,
          error_responses: 0
        }
      }),
      Promise.race([
        configService.getAllConfigs(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('超时')), timeout))
      ]).catch((err) => {
        console.warn('获取配置数据失败:', err)
        return {
          system_name: "AI灵魂伙伴",
          version: "1.0.0",
          debug_mode: true,
          max_sessions_per_user: 10,
          default_prompt_version: "v1"
        }
      }),
      Promise.race([
        configService.getPromptVersions(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('超时')), timeout))
      ]).catch((err) => {
        console.warn('获取提示词版本失败:', err)
        return {
          versions: ["v1", "v2"],
          current_default: "v1"
        }
      }),
      Promise.race([
        configService.getPromptUsageStats(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('超时')), timeout))
      ]).catch((err) => {
        console.warn('获取提示词使用统计失败:', err)
        return {
          prompt_usage: {},
          total_usage: 0
        }
      })
    ])

    stats.value = statsData
    performance.value = performanceData
    configs.value = configsData
    promptVersions.value = versionsData
    promptUsageStats.value = usageData
    
    console.log('系统数据加载完成:', {
      stats: statsData,
      performance: performanceData,
      configs: configsData
    })
  } catch (err) {
    console.error('加载数据失败:', err)
    error.value = '加载系统数据失败，显示默认配置'
    
    // 设置默认值
    stats.value = {
      today: {
        sessions_created: 0,
        messages_processed: 0,
        successful_responses: 0,
        error_responses: 0,
        cache_hits: 0,
        chat_sessions_joined: 0
      },
      trends: {}
    }
    performance.value = {
      cache_hit_rate: 0,
      success_rate: 0,
      total_requests: 0,
      cache_hits: 0,
      successful_responses: 0,
      error_responses: 0
    }
    configs.value = {
      system_name: "AI灵魂伙伴",
      version: "1.0.0",
      debug_mode: true,
      max_sessions_per_user: 10,
      default_prompt_version: "v1"
    }
    promptVersions.value = {
      versions: ["v1", "v2"],
      current_default: "v1"
    }
    promptUsageStats.value = {
      prompt_usage: {},
      total_usage: 0
    }
  } finally {
    loading.value = false
  }
}

// 加载攻略对象数据
const loadCompanions = async () => {
  companionsLoading.value = true
  try {
    console.log('开始加载攻略对象...')
    
    // 设置超时时间
    const timeout = 5000 // 5秒超时
    
    // 只加载系统预设的攻略对象
    const systemResponse = await Promise.race([
      api.get('/companions/system'),
      new Promise((_, reject) => setTimeout(() => reject(new Error('超时')), timeout))
    ])
    
    systemCompanions.value = (systemResponse as any).data || systemResponse
    console.log('攻略对象加载完成:', systemCompanions.value)
  } catch (error) {
    console.error('加载攻略对象失败:', error)
    systemCompanions.value = []
  } finally {
    companionsLoading.value = false
  }
}

// 开始攻略
const startChat = (companion: any) => {
  // 跳转到聊天页面开始攻略
  window.location.href = `/#/chat/${companion.id}`
}

const editConfig = (key: string, value: any) => {
  configForm.value = {
    key,
    value: typeof value === 'object' ? JSON.stringify(value, null, 2) : value.toString(),
    ttl: null
  }
  editingConfig.value = true
}

const deleteConfig = async (key: string) => {
  if (confirm(`确定要删除配置 "${key}" 吗？`)) {
    try {
      await configService.deleteConfig(key)
      await loadData()
    } catch (error) {
      console.error('删除配置失败:', error)
    }
  }
}

const saveConfig = async () => {
  try {
    let value: any = configForm.value.value
    
    // 尝试解析 JSON
    try {
      value = JSON.parse(value)
    } catch {
      // 保持原始字符串值
    }

    await configService.setConfig(configForm.value.key, value, configForm.value.ttl || undefined)
    await loadData()
    cancelConfigEdit()
  } catch (error) {
    console.error('保存配置失败:', error)
  }
}

const cancelConfigEdit = () => {
  showAddConfig.value = false
  editingConfig.value = false
  configForm.value = { key: '', value: '', ttl: null }
}

const exportConversations = async () => {
  exporting.value = true
  try {
    const params: any = {}
    if (exportForm.value.userId) params.userId = exportForm.value.userId
    if (exportForm.value.startDate) params.startDate = exportForm.value.startDate
    if (exportForm.value.endDate) params.endDate = exportForm.value.endDate
    
    const response = await configService.exportConversations(params)
    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `conversations_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出对话记录失败:', error)
  } finally {
    exporting.value = false
  }
}

const exportStats = async () => {
  try {
    const statsData = {
      overview: stats.value,
      performance: performance.value,
      timestamp: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(statsData, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `system_stats_${new Date().toISOString().split('T')[0]}.json`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出统计数据失败:', error)
  }
}

// 初始化
onMounted(() => {
  console.log('SystemSettings页面已挂载，开始加载数据...')
  loadData()
  loadCompanions()
  // 每30秒刷新一次数据
  setInterval(loadData, 30000)
})
</script>
