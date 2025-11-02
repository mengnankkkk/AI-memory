<template>
  <Transition name="viewer">
    <div v-if="visible" class="image-viewer-overlay" @click="handleClose">
      <div class="viewer-container" @click.stop>
        <!-- 关闭按钮 -->
        <button class="close-btn" @click="handleClose">
          <span class="close-icon">✕</span>
        </button>

        <!-- 视频展示 -->
        <div v-if="isVideo" class="video-wrapper">
          <video
            ref="videoRef"
            :src="mediaUrl"
            class="viewer-video"
            controls
            autoplay
            loop
            @error="handleMediaError"
          ></video>
          <div class="media-title">
            <span class="title-icon">👑</span>
            <span>完美结局 - {{ companionName }}</span>
          </div>
        </div>

        <!-- 图片展示 -->
        <div v-else class="image-wrapper">
          <img
            :src="mediaUrl"
            :alt="mediaTitle"
            class="viewer-image"
            @error="handleMediaError"
          />
          <div class="media-title">
            <span class="title-icon">{{ levelIcon }}</span>
            <span>{{ mediaTitle }}</span>
          </div>
        </div>

        <!-- 等级信息 -->
        <div class="level-info-badge" v-if="!isVideo">
          <span class="badge-label">{{ levelName }}</span>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { AFFINITY_LEVELS, LEVEL_ORDER } from '@/config/affinity-config'

interface Props {
  visible: boolean
  mediaUrl: string
  levelNumber: number
  companionId: number
  companionName: string
  isVideo?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isVideo: false
})

const emit = defineEmits<{
  close: []
}>()

const videoRef = ref<HTMLVideoElement | null>(null)
const imageError = ref(false)

// 计算等级信息
const levelKey = computed(() => {
  if (props.levelNumber < 1 || props.levelNumber > 7) return 'stranger'
  return LEVEL_ORDER[props.levelNumber - 1]
})

const levelConfig = computed(() => {
  return AFFINITY_LEVELS[levelKey.value]
})

const levelName = computed(() => levelConfig.value?.name || '未知')
const levelIcon = computed(() => levelConfig.value?.icon || '❤️')

const mediaTitle = computed(() => {
  return `${props.companionName} - ${levelName.value}`
})

// 监听visible变化，重置错误状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    imageError.value = false
    if (props.isVideo && videoRef.value) {
      videoRef.value.play().catch(err => {
        console.log('视频自动播放失败:', err)
      })
    }
  }
})

// 处理媒体加载错误
const handleMediaError = (e: Event) => {
  console.log('图片加载失败:', props.mediaUrl)
  imageError.value = true
  // 不自动重试，避免无限循环
  // 图片错误已在ImageGallerySidebar中处理
}

const handleClose = () => {
  // 如果是视频，停止播放
  if (props.isVideo && videoRef.value) {
    videoRef.value.pause()
  }
  imageError.value = false
  emit('close')
}

// ESC键关闭
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && props.visible) {
    handleClose()
  }
}

// 监听键盘事件
watch(() => props.visible, (newVal) => {
  if (newVal) {
    document.addEventListener('keydown', handleKeydown)
  } else {
    document.removeEventListener('keydown', handleKeydown)
  }
})
</script>

<style scoped>
.image-viewer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.viewer-container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: zoomIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale(0.7);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  top: -50px;
  right: 0;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: scale(1.1) rotate(90deg);
}

.close-icon {
  font-size: 24px;
  color: white;
  font-weight: 300;
}

/* 图片包装器 */
.image-wrapper {
  position: relative;
  max-width: 100%;
  max-height: calc(90vh - 80px);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.viewer-image {
  max-width: 100%;
  max-height: calc(90vh - 80px);
  width: auto;
  height: auto;
  display: block;
  border-radius: 16px;
  object-fit: contain;
}

/* 视频包装器 */
.video-wrapper {
  position: relative;
  max-width: 100%;
  max-height: calc(90vh - 80px);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  background: black;
}

.viewer-video {
  max-width: 100%;
  max-height: calc(90vh - 80px);
  width: auto;
  height: auto;
  display: block;
  border-radius: 16px;
}

/* 媒体标题 */
.media-title {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9), transparent);
  color: white;
  padding: 24px 20px 20px;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 0 0 16px 16px;
}

.title-icon {
  font-size: 24px;
}

/* 等级信息徽章 */
.level-info-badge {
  position: absolute;
  top: 20px;
  left: 20px;
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  padding: 8px 20px;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.4);
  animation: badgeSlide 0.5s ease-out 0.2s backwards;
}

@keyframes badgeSlide {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.badge-label {
  color: white;
  font-size: 14px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* 过渡动画 */
.viewer-enter-active,
.viewer-leave-active {
  transition: opacity 0.3s ease;
}

.viewer-enter-from,
.viewer-leave-to {
  opacity: 0;
}

.viewer-enter-active .viewer-container {
  animation: zoomIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.viewer-leave-active .viewer-container {
  animation: zoomOut 0.3s ease;
}

@keyframes zoomOut {
  from {
    opacity: 1;
    transform: scale(1);
  }
  to {
    opacity: 0;
    transform: scale(0.8);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .close-btn {
    top: -60px;
    right: 10px;
  }

  .media-title {
    font-size: 16px;
    padding: 20px 16px 16px;
  }

  .title-icon {
    font-size: 20px;
  }

  .level-info-badge {
    top: 10px;
    left: 10px;
    padding: 6px 16px;
  }

  .badge-label {
    font-size: 12px;
  }
}
</style>
