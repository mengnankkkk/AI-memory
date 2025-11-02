<template>
  <div class="image-gallery-sidebar">
    <!-- 侧边栏头部 -->
    <div class="sidebar-header">
      <h3 class="sidebar-title">
        <span class="icon">🖼️</span>
        <span>回忆收集</span>
      </h3>
      <button
        @click="toggleSidebar"
        class="toggle-btn"
        :class="{ 'collapsed': isCollapsed }"
      >
        {{ isCollapsed ? '◀' : '▶' }}
      </button>
    </div>

    <!-- 图片网格 -->
    <transition name="slide">
      <div v-if="!isCollapsed" class="gallery-grid">
        <div
          v-for="level in 7"
          :key="level"
          class="gallery-item"
          :class="{ 'unlocked': isLevelUnlocked(level), 'current': isCurrentLevel(level) }"
        >
          <!-- 已解锁：显示图片 -->
          <div
            v-if="isLevelUnlocked(level)"
            class="image-container"
            @click="openImageViewer(level)"
          >
            <img
              :src="getLevelImage(level)"
              :alt="`等级${level}回忆`"
              class="gallery-image"
              @load="handleImageLoad($event, level)"
              @error="handleImageError($event, level)"
            />
            <div class="image-overlay">
              <span class="level-badge">{{ getLevelName(level) }}</span>
            </div>
            <!-- 当前等级标记 -->
            <div v-if="isCurrentLevel(level)" class="current-marker">
              <span class="marker-icon">✨</span>
            </div>
          </div>

          <!-- 未解锁：显示锁定状态 -->
          <div v-else class="locked-container">
            <div class="lock-icon">🔒</div>
            <div class="lock-text">{{ getLevelName(level) }}</div>
            <div class="unlock-hint">好感度 {{ getLevelThreshold(level) }}</div>
          </div>
        </div>

        <!-- 满级特殊位置：视频 -->
        <div
          class="gallery-item special-item"
          :class="{ 'unlocked': affinity >= 1000 }"
        >
          <div v-if="affinity >= 1000" class="video-container" @click="openVideoViewer">
            <video
              :src="getEndVideo()"
              class="gallery-video"
              loop
              muted
              @mouseenter="$event.target.play()"
              @mouseleave="$event.target.pause()"
            ></video>
            <div class="video-overlay">
              <span class="level-badge special">🎊 完美结局</span>
            </div>
          </div>
          <div v-else class="locked-container special-locked">
            <div class="lock-icon">👑</div>
            <div class="lock-text">完美结局</div>
            <div class="unlock-hint">好感度 1000</div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 收集进度 -->
    <transition name="fade">
      <div v-if="!isCollapsed" class="progress-section">
        <div class="progress-label">
          <span>收集进度</span>
          <span class="progress-count">{{ unlockedCount }}/8</span>
        </div>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${(unlockedCount / 8) * 100}%` }"
          ></div>
        </div>
      </div>
    </transition>

    <!-- 图片/视频查看器 -->
    <ImageViewer
      :visible="showViewer"
      :media-url="viewerMediaUrl"
      :level-number="viewerLevelNumber"
      :companion-id="companionId"
      :companion-name="companionName"
      :is-video="viewerIsVideo"
      @close="closeViewer"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { AFFINITY_LEVELS, LEVEL_ORDER } from '@/config/affinity-config'
import { getRandomLevelImage, getLevelNumber } from '@/utils/image-loader'
import ImageViewer from './ImageViewer.vue'

interface Props {
  companionId: number
  companionName: string
  currentLevel: string
  affinity: number
}

const props = defineProps<Props>()

// 侧边栏折叠状态
const isCollapsed = ref(false)

// 图片加载失败记录
const failedImages = ref<Record<number, number>>({})

// 成功加载的图片URL缓存
const successfulImages = ref<Record<number, string>>({})

// 查看器状态
const showViewer = ref(false)
const viewerMediaUrl = ref('')
const viewerLevelNumber = ref(1)
const viewerIsVideo = ref(false)

// 切换侧边栏
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

// 判断等级是否解锁
const isLevelUnlocked = (level: number): boolean => {
  const currentLevelIndex = LEVEL_ORDER.indexOf(props.currentLevel)
  return level <= currentLevelIndex + 1
}

// 判断是否为当前等级
const isCurrentLevel = (level: number): boolean => {
  const currentLevelIndex = LEVEL_ORDER.indexOf(props.currentLevel)
  return level === currentLevelIndex + 1
}

// 获取等级名称
const getLevelName = (level: number): string => {
  if (level < 1 || level > 7) return '未知'
  const levelKey = LEVEL_ORDER[level - 1]
  return AFFINITY_LEVELS[levelKey]?.name || '未知'
}

// 获取等级阈值
const getLevelThreshold = (level: number): number => {
  if (level < 1 || level > 7) return 0
  const levelKey = LEVEL_ORDER[level - 1]
  return AFFINITY_LEVELS[levelKey]?.minScore || 0
}

// 获取等级图片
const getLevelImage = (level: number): string => {
  // 如果有缓存的成功URL，直接使用
  if (successfulImages.value[level]) {
    return successfulImages.value[level]
  }

  const levelKey = LEVEL_ORDER[level - 1]
  return getRandomLevelImage(props.companionId, levelKey, props.affinity)
}

// 图片加载成功，缓存URL
const handleImageLoad = (e: Event, level: number) => {
  const target = e.target as HTMLImageElement
  successfulImages.value[level] = target.src
  // 清除失败计数
  if (failedImages.value[level]) {
    delete failedImages.value[level]
  }
}

// 获取结局视频
const getEndVideo = (): string => {
  const characterFolderMap: Record<number, string> = {
    1: 'linzixi',
    2: 'xuejian',
    3: 'nagi',
    4: 'shiyu',
    5: 'zoe',
    6: 'kevin'
  }
  const folder = characterFolderMap[props.companionId] || 'nagi'
  return `/img/${folder}/end.mp4`
}

// 点击图片打开查看器
const openImageViewer = (level: number) => {
  if (!isLevelUnlocked(level)) return

  viewerMediaUrl.value = getLevelImage(level)
  viewerLevelNumber.value = level
  viewerIsVideo.value = false
  showViewer.value = true
}

// 点击视频打开查看器
const openVideoViewer = () => {
  if (props.affinity < 1000) return

  viewerMediaUrl.value = getEndVideo()
  viewerLevelNumber.value = 0 // 特殊标记为满级
  viewerIsVideo.value = true
  showViewer.value = true
}

// 关闭查看器
const closeViewer = () => {
  showViewer.value = false
}

// 处理图片加载错误
const handleImageError = (e: Event, level: number) => {
  const target = e.target as HTMLImageElement
  const attemptCount = failedImages.value[level] || 0

  if (attemptCount < 9) {
    // 重试加载不同的图片变体
    const characterFolderMap: Record<number, string> = {
      1: 'linzixi',
      2: 'xuejian',
      3: 'nagi',
      4: 'shiyu',
      5: 'zoe',
      6: 'kevin'
    }
    const folder = characterFolderMap[props.companionId] || 'nagi'

    // 循环尝试不同的索引和格式
    const extensions = ['jpeg', 'jpg', 'png']
    const indexToTry = attemptCount % 3  // 0, 1, 2
    const extToTry = extensions[Math.floor(attemptCount / 3)]  // jpeg, jpg, png

    target.src = `/img/${folder}/${level}-${indexToTry}.${extToTry}`
    failedImages.value[level] = attemptCount + 1

    console.log(`尝试加载图片 (${attemptCount + 1}/9):`, target.src)
  } else {
    // 使用默认占位图
    console.log('所有图片加载失败，使用占位图')
    target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f3f4f6" width="200" height="200"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle" fill="%239ca3af" font-size="24"%3E❤️%3C/text%3E%3C/svg%3E'
  }
}

// 已解锁数量
const unlockedCount = computed(() => {
  const currentLevelIndex = LEVEL_ORDER.indexOf(props.currentLevel)
  let count = currentLevelIndex + 1
  if (props.affinity >= 1000) count += 1
  return count
})
</script>

<style scoped>
.image-gallery-sidebar {
  width: 280px;
  background: linear-gradient(180deg, #fdf4f8 0%, #f9fafb 100%);
  border-right: 2px solid #fce7f3;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.3s ease;
}

.image-gallery-sidebar.collapsed {
  width: 60px;
}

/* 头部 */
.sidebar-header {
  padding: 16px;
  background: white;
  border-bottom: 2px solid #fce7f3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #ec4899;
  margin: 0;
}

.sidebar-title .icon {
  font-size: 20px;
}

.toggle-btn {
  padding: 6px;
  background: #fce7f3;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #ec4899;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background: #fbcfe8;
  transform: scale(1.1);
}

/* 图片网格 */
.gallery-grid {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.gallery-grid::-webkit-scrollbar {
  width: 6px;
}

.gallery-grid::-webkit-scrollbar-thumb {
  background: #fce7f3;
  border-radius: 3px;
}

.gallery-item {
  aspect-ratio: 3 / 4;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
}

.gallery-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(236, 72, 153, 0.3);
}

.gallery-item.current {
  box-shadow: 0 0 0 3px #ec4899;
  animation: pulse-border 2s ease-in-out infinite;
}

@keyframes pulse-border {
  0%, 100% {
    box-shadow: 0 0 0 3px #ec4899;
  }
  50% {
    box-shadow: 0 0 0 5px #ec4899, 0 0 20px rgba(236, 72, 153, 0.5);
  }
}

.image-container {
  width: 100%;
  height: 100%;
  position: relative;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.image-container:hover {
  transform: scale(1.05);
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
  padding: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-container:hover .image-overlay {
  opacity: 1;
}

.level-badge {
  display: inline-block;
  background: white;
  color: #ec4899;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.level-badge.special {
  background: linear-gradient(135deg, #f59e0b, #ec4899);
  color: white;
}

.current-marker {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #ec4899;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: bounce 2s ease-in-out infinite;
}

.marker-icon {
  font-size: 18px;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

/* 锁定容器 */
.locked-container {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
}

.locked-container.special-locked {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.lock-icon {
  font-size: 36px;
  opacity: 0.5;
}

.lock-text {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
}

.unlock-hint {
  font-size: 11px;
  color: #9ca3af;
}

/* 视频容器 */
.video-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: black;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.video-container:hover {
  transform: scale(1.05);
}

.gallery-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  padding: 12px;
}

/* 进度区域 */
.progress-section {
  padding: 16px;
  background: white;
  border-top: 2px solid #fce7f3;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
  font-weight: 600;
}

.progress-count {
  color: #ec4899;
  font-weight: 700;
}

.progress-bar {
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ec4899 0%, #f472b6 100%);
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* 过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 1024px) {
  .image-gallery-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.1);
  }

  .image-gallery-sidebar.collapsed {
    width: 50px;
  }
}
</style>
