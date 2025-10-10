<template>
  <div class="companion-avatar" :class="sizeClass">
    <div class="avatar-container" :style="containerStyle">
      <!-- 头像图片 -->
      <img
        :src="avatarUrl"
        :alt="`${companionName} - ${levelConfig?.name}`"
        class="avatar-image"
        @error="handleImageError"
        @load="handleImageLoad"
      />

      <!-- 加载中占位符 -->
      <div v-if="isLoading" class="avatar-placeholder">
        <div class="spinner"></div>
      </div>

      <!-- 等级标识 -->
      <div v-if="showLevelBadge && levelConfig" class="level-badge" :style="badgeStyle">
        <span class="level-icon">{{ levelConfig.icon }}</span>
        <span v-if="size === 'large'" class="level-name">{{ levelConfig.name }}</span>
      </div>

      <!-- 好感度进度环（可选） -->
      <div v-if="showProgress && levelProgress !== null" class="progress-ring">
        <svg :width="progressRingSize" :height="progressRingSize">
          <circle
            class="progress-ring-bg"
            :cx="progressRingSize / 2"
            :cy="progressRingSize / 2"
            :r="progressRadius"
            :stroke-width="progressStroke"
            fill="none"
          />
          <circle
            class="progress-ring-fill"
            :cx="progressRingSize / 2"
            :cy="progressRingSize / 2"
            :r="progressRadius"
            :stroke-width="progressStroke"
            fill="none"
            :stroke="levelConfig?.color || '#6b7280'"
            :stroke-dasharray="progressCircumference"
            :stroke-dashoffset="progressOffset"
          />
        </svg>
      </div>
    </div>

    <!-- 动画效果层 -->
    <transition name="affinity-glow">
      <div v-if="showGlow" class="affinity-glow" :style="{ background: levelConfig?.color }"></div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getLevelConfig, getLevelProgress, getCompanionAvatar, type AffinityLevelConfig } from '@/config/affinity-config'

interface Props {
  companionId: string
  companionName?: string
  levelKey?: string
  affinityScore?: number
  size?: 'small' | 'medium' | 'large' | 'xlarge'
  showLevelBadge?: boolean
  showProgress?: boolean
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  companionName: '',
  levelKey: 'stranger',
  affinityScore: 50,
  size: 'medium',
  showLevelBadge: true,
  showProgress: false,
  animated: true
})

const isLoading = ref(true)
const imageError = ref(false)
const showGlow = ref(false)

// 计算等级配置
const levelConfig = computed<AffinityLevelConfig>(() => {
  return getLevelConfig(props.levelKey || 'stranger')
})

// 计算等级进度
const levelProgress = computed(() => {
  if (props.affinityScore === undefined) return null
  return getLevelProgress(props.affinityScore, props.levelKey || 'stranger')
})

// 头像URL
const avatarUrl = computed(() => {
  if (imageError.value) {
    // 如果等级特定头像加载失败，使用基础头像
    return `/img/${props.companionId}.png`
  }
  return getCompanionAvatar(props.companionId, props.levelKey)
})

// 尺寸类
const sizeClass = computed(() => `avatar-${props.size}`)

// 容器样式
const containerStyle = computed(() => ({
  borderColor: levelConfig.value?.color || '#6b7280'
}))

// 标签样式
const badgeStyle = computed(() => ({
  backgroundColor: levelConfig.value?.bgColor || '#e5e7eb',
  color: levelConfig.value?.color || '#6b7280'
}))

// 进度环尺寸
const progressRingSize = computed(() => {
  const sizes = { small: 80, medium: 120, large: 160, xlarge: 200 }
  return sizes[props.size]
})

const progressRadius = computed(() => progressRingSize.value / 2 - 8)
const progressStroke = computed(() => (props.size === 'small' ? 3 : 4))
const progressCircumference = computed(() => 2 * Math.PI * progressRadius.value)
const progressOffset = computed(() => {
  if (levelProgress.value === null) return progressCircumference.value
  const progress = levelProgress.value / 100
  return progressCircumference.value * (1 - progress)
})

// 图片加载处理
const handleImageLoad = () => {
  isLoading.value = false
  if (props.animated) {
    showGlow.value = true
    setTimeout(() => {
      showGlow.value = false
    }, 1000)
  }
}

const handleImageError = () => {
  if (!imageError.value) {
    // 第一次失败，尝试加载基础头像
    imageError.value = true
  } else {
    // 基础头像也失败，停止加载
    isLoading.value = false
  }
}

// 监听等级变化，触发动画
watch(() => props.levelKey, (newLevel, oldLevel) => {
  if (oldLevel && newLevel !== oldLevel && props.animated) {
    showGlow.value = true
    setTimeout(() => {
      showGlow.value = false
    }, 1500)
  }
})
</script>

<style scoped>
.companion-avatar {
  position: relative;
  display: inline-block;
}

.avatar-container {
  position: relative;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid;
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
  transition: all 0.3s ease;
}

.avatar-container:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
}

.spinner {
  width: 30%;
  height: 30%;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: #333;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.level-badge {
  position: absolute;
  bottom: 8%;
  right: 8%;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 2;
}

.level-icon {
  font-size: 1rem;
}

.level-name {
  white-space: nowrap;
}

.progress-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.progress-ring-bg {
  stroke: rgba(0, 0, 0, 0.1);
}

.progress-ring-fill {
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
  transition: stroke-dashoffset 0.5s ease;
}

.affinity-glow {
  position: absolute;
  top: -10%;
  left: -10%;
  width: 120%;
  height: 120%;
  border-radius: 50%;
  opacity: 0.4;
  filter: blur(20px);
  z-index: -1;
}

.affinity-glow-enter-active,
.affinity-glow-leave-active {
  transition: opacity 0.8s ease, transform 0.8s ease;
}

.affinity-glow-enter-from {
  opacity: 0;
  transform: scale(0.8);
}

.affinity-glow-enter-to {
  opacity: 0.6;
  transform: scale(1.2);
}

.affinity-glow-leave-from {
  opacity: 0.6;
  transform: scale(1.2);
}

.affinity-glow-leave-to {
  opacity: 0;
  transform: scale(1.4);
}

/* 尺寸变体 */
.avatar-small .avatar-container {
  width: 60px;
  height: 60px;
  border-width: 2px;
}

.avatar-small .level-badge {
  padding: 2px 6px;
  font-size: 0.625rem;
}

.avatar-small .level-icon {
  font-size: 0.875rem;
}

.avatar-medium .avatar-container {
  width: 100px;
  height: 100px;
  border-width: 3px;
}

.avatar-large .avatar-container {
  width: 140px;
  height: 140px;
  border-width: 4px;
}

.avatar-large .level-badge {
  padding: 6px 12px;
  font-size: 0.875rem;
}

.avatar-large .level-icon {
  font-size: 1.25rem;
}

.avatar-xlarge .avatar-container {
  width: 180px;
  height: 180px;
  border-width: 5px;
}

.avatar-xlarge .level-badge {
  padding: 8px 16px;
  font-size: 1rem;
}

.avatar-xlarge .level-icon {
  font-size: 1.5rem;
}
</style>
