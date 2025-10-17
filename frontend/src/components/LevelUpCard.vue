<template>
  <Transition name="levelup">
    <div v-if="visible" class="levelup-overlay" @click="close">
      <div class="levelup-card" @click.stop>
        <!-- 背景装饰 -->
        <div class="bg-decoration">
          <div class="light-ray" v-for="i in 12" :key="i" :style="getRayStyle(i)"></div>
        </div>

        <!-- 关系等级标题 -->
        <div class="level-header">
          <div class="level-badge">
            <div class="badge-icon">💕</div>
            <div class="badge-text">关系升级</div>
          </div>
        </div>

        <!-- 人物立绘 -->
        <div class="character-portrait">
          <div class="portrait-frame">
            <img
              :src="characterImage"
              :alt="companionName"
              class="portrait-image"
              @error="handleImageError"
            />
            <div class="portrait-glow"></div>
          </div>
        </div>

        <!-- 等级信息 -->
        <div class="level-info">
          <div class="level-transition">
            <div class="old-level">{{ oldLevelName }}</div>
            <div class="arrow">
              <i class="fas fa-arrow-right"></i>
            </div>
            <div class="new-level">{{ newLevelName }}</div>
          </div>

          <div class="level-description">
            {{ levelDescription }}
          </div>

          <div class="affinity-info">
            <span class="affinity-label">当前好感度</span>
            <span class="affinity-value">{{ currentAffinity }}</span>
          </div>
        </div>

        <!-- 关系解锁内容 -->
        <div v-if="unlockedFeatures.length > 0" class="unlocked-features">
          <div class="features-title">🎁 解锁新内容</div>
          <div class="features-list">
            <div
              v-for="(feature, index) in unlockedFeatures"
              :key="index"
              class="feature-item"
              :style="{ animationDelay: `${index * 0.1}s` }"
            >
              <i class="fas fa-star"></i>
              <span>{{ feature }}</span>
            </div>
          </div>
        </div>

        <!-- 继续按钮 -->
        <button class="continue-button" @click="close">
          <span>继续相处</span>
          <i class="fas fa-heart"></i>
        </button>

        <!-- 粒子特效 -->
        <div class="particles">
          <div
            v-for="i in 30"
            :key="i"
            class="particle"
            :style="getParticleStyle(i)"
          ></div>
        </div>

        <!-- 心形特效 -->
        <div class="hearts">
          <div
            v-for="i in 8"
            :key="i"
            class="heart"
            :style="getHeartStyle(i)"
          >💗</div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getLevelConfig } from '@/config/affinity-config'

interface Props {
  visible: boolean
  companionId: number
  companionName: string
  oldLevel: string
  newLevel: string
  currentAffinity: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

// 角色立绘映射（ID -> 文件夹名）
const characterFolderMap: Record<number, string> = {
  1: 'nagi',      // 娜姬
  2: 'xuejian',   // 雪见
  3: 'zoe',       // Zoe
  4: 'shiyu',     // 诗雨
  5: 'linzixi',   // 林子晞
  6: 'kevin'      // Kevin
}

// 等级到立绘的映射
const levelImageMap: Record<string, string> = {
  'stranger': 'C1-0.jpg',         // 陌生人
  'acquaintance': 'C1-1.jpg',     // 相识
  'friend': 'C2-0.jpg',           // 朋友
  'close_friend': 'C2-1.jpg',     // 密友
  'special': 'C3-0.jpg',          // 特别关系
  'romantic': 'C3-1.jpg',         // 暧昧
  'lover': 'C4-0.jpg'             // 恋人
}

// 计算角色立绘路径
const characterImage = computed(() => {
  const folder = characterFolderMap[props.companionId] || 'nagi'
  const imageFile = levelImageMap[props.newLevel] || 'C1-0.jpg'
  return `/img/${folder}/${imageFile}`
})

// 等级配置
const oldLevelConfig = computed(() => getLevelConfig(props.oldLevel))
const newLevelConfig = computed(() => getLevelConfig(props.newLevel))

const oldLevelName = computed(() => oldLevelConfig.value.name)
const newLevelName = computed(() => newLevelConfig.value.name)
const levelDescription = computed(() => newLevelConfig.value.description)

// 解锁的新功能
const unlockedFeatures = computed(() => {
  const features: string[] = []

  // 根据不同等级解锁不同内容
  switch (props.newLevel) {
    case 'acquaintance':
      features.push('可以赠送普通礼物', '解锁更多聊天话题')
      break
    case 'friend':
      features.push('可以赠送稀有礼物', '解锁亲密互动', '每日任务增加')
      break
    case 'close_friend':
      features.push('可以赠送史诗礼物', '解锁特殊事件', '好感度加成提升')
      break
    case 'special':
      features.push('可以赠送传说礼物', '解锁专属剧情', '特殊称呼')
      break
    case 'romantic':
      features.push('解锁浪漫互动', '专属约会场景', '心意表达')
      break
    case 'lover':
      features.push('解锁恋人专属剧情', '亲密度上限提升', '永久纪念')
      break
  }

  return features
})

const close = () => {
  emit('close')
}

const handleImageError = (e: Event) => {
  // 图片加载失败时使用默认图片
  const target = e.target as HTMLImageElement
  target.src = '/img/nagi/C1-0.jpg'
}

// 光线样式
const getRayStyle = (index: number) => {
  const angle = (index / 12) * 360
  return {
    transform: `rotate(${angle}deg)`,
    animationDelay: `${index * 0.1}s`
  }
}

// 粒子样式
const getParticleStyle = (index: number) => {
  const angle = (index / 30) * 360
  const distance = Math.random() * 200 + 150
  const x = Math.cos((angle * Math.PI) / 180) * distance
  const y = Math.sin((angle * Math.PI) / 180) * distance

  return {
    left: '50%',
    top: '50%',
    '--tx': `${x}px`,
    '--ty': `${y}px`,
    animationDelay: `${index * 0.05}s`,
    animationDuration: `${1 + Math.random() * 0.5}s`
  }
}

// 心形样式
const getHeartStyle = (index: number) => {
  const angle = (index / 8) * 360
  const distance = 120
  const x = Math.cos((angle * Math.PI) / 180) * distance
  const y = Math.sin((angle * Math.PI) / 180) * distance

  return {
    left: '50%',
    top: '50%',
    '--hx': `${x}px`,
    '--hy': `${y}px`,
    animationDelay: `${index * 0.15}s`
  }
}
</script>

<style scoped>
.levelup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.levelup-card {
  position: relative;
  background: linear-gradient(135deg, #fff 0%, #ffe5f1 100%);
  border-radius: 32px;
  max-width: 600px;
  width: 100%;
  overflow: hidden;
  box-shadow:
    0 30px 90px rgba(255, 105, 180, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.9);
  animation: cardEntrance 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes cardEntrance {
  from {
    opacity: 0;
    transform: scale(0.5) translateY(100px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.light-ray {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 50%;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.8), transparent);
  transform-origin: top center;
  animation: rayPulse 3s ease-in-out infinite;
}

@keyframes rayPulse {
  0%, 100% {
    opacity: 0.3;
    height: 50%;
  }
  50% {
    opacity: 0.8;
    height: 60%;
  }
}

/* 等级标题 */
.level-header {
  padding: 32px 32px 0;
  text-align: center;
}

.level-badge {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  padding: 12px 32px;
  border-radius: 50px;
  box-shadow: 0 8px 24px rgba(236, 72, 153, 0.4);
  animation: badgeBounce 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s backwards;
}

@keyframes badgeBounce {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.badge-icon {
  font-size: 2rem;
  animation: iconSpin 2s ease-in-out infinite;
}

@keyframes iconSpin {
  0%, 100% {
    transform: rotate(0deg) scale(1);
  }
  50% {
    transform: rotate(15deg) scale(1.2);
  }
}

.badge-text {
  color: white;
  font-size: 1.25rem;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 人物立绘 */
.character-portrait {
  padding: 32px;
  display: flex;
  justify-content: center;
}

.portrait-frame {
  position: relative;
  width: 100%;
  max-width: 400px;
  aspect-ratio: 3 / 4;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: portraitReveal 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.5s backwards;
}

@keyframes portraitReveal {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(50px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.portrait-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  animation: imageZoom 20s ease-in-out infinite;
}

@keyframes imageZoom {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.portrait-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg,
    rgba(255, 105, 180, 0.2) 0%,
    transparent 50%,
    rgba(147, 51, 234, 0.2) 100%);
  pointer-events: none;
  animation: glowPulse 3s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 0.8;
  }
}

/* 等级信息 */
.level-info {
  padding: 0 32px 24px;
  text-align: center;
}

.level-transition {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
  animation: levelSlide 0.8s ease-out 0.7s backwards;
}

@keyframes levelSlide {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.old-level {
  font-size: 1.25rem;
  color: #9ca3af;
  text-decoration: line-through;
  opacity: 0.6;
}

.arrow {
  color: #f472b6;
  font-size: 1.5rem;
  animation: arrowBounce 1s ease-in-out infinite;
}

@keyframes arrowBounce {
  0%, 100% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(8px);
  }
}

.new-level {
  font-size: 1.75rem;
  font-weight: 700;
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.level-description {
  font-size: 1rem;
  color: #6b7280;
  margin-bottom: 16px;
  line-height: 1.6;
  animation: textFade 0.8s ease-out 0.9s backwards;
}

@keyframes textFade {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.affinity-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: white;
  padding: 12px 24px;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  animation: affinityPop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 1.1s backwards;
}

@keyframes affinityPop {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.affinity-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.affinity-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f472b6;
}

/* 解锁内容 */
.unlocked-features {
  padding: 0 32px 24px;
  animation: featuresFade 0.8s ease-out 1.3s backwards;
}

@keyframes featuresFade {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.features-title {
  text-align: center;
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.8);
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.875rem;
  color: #374151;
  animation: featureSlide 0.5s ease-out backwards;
}

@keyframes featureSlide {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.feature-item i {
  color: #fbbf24;
  font-size: 1rem;
}

/* 继续按钮 */
.continue-button {
  width: calc(100% - 64px);
  margin: 0 32px 32px;
  padding: 16px;
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  box-shadow: 0 8px 24px rgba(236, 72, 153, 0.4);
  transition: all 0.3s ease;
  animation: buttonPulse 2s ease-in-out 1.5s infinite;
}

@keyframes buttonPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 8px 24px rgba(236, 72, 153, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 12px 32px rgba(236, 72, 153, 0.6);
  }
}

.continue-button:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 32px rgba(236, 72, 153, 0.6);
}

.continue-button:active {
  transform: scale(0.98);
}

/* 粒子效果 */
.particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.particle {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: radial-gradient(circle, #fbbf24, #f59e0b);
  animation: particleFloat 1.5s ease-out forwards;
  opacity: 0;
}

@keyframes particleFloat {
  0% {
    opacity: 0;
    transform: translate(0, 0) scale(0);
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translate(var(--tx), var(--ty)) scale(1);
  }
}

/* 心形效果 */
.hearts {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.heart {
  position: absolute;
  font-size: 2rem;
  animation: heartFloat 2s ease-out forwards;
  opacity: 0;
}

@keyframes heartFloat {
  0% {
    opacity: 0;
    transform: translate(0, 0) scale(0) rotate(0deg);
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translate(var(--hx), var(--hy)) scale(1.5) rotate(360deg);
  }
}

/* 过渡动画 */
.levelup-enter-active,
.levelup-leave-active {
  transition: opacity 0.5s ease;
}

.levelup-enter-from,
.levelup-leave-to {
  opacity: 0;
}

.levelup-enter-active .levelup-card {
  animation: cardEntrance 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.levelup-leave-active .levelup-card {
  animation: cardExit 0.5s ease;
}

@keyframes cardExit {
  from {
    opacity: 1;
    transform: scale(1);
  }
  to {
    opacity: 0;
    transform: scale(0.9);
  }
}

/* 响应式 */
@media (max-width: 640px) {
  .levelup-card {
    border-radius: 24px;
  }

  .level-header,
  .character-portrait,
  .level-info,
  .unlocked-features {
    padding-left: 24px;
    padding-right: 24px;
  }

  .portrait-frame {
    max-width: 300px;
  }

  .badge-text {
    font-size: 1rem;
  }

  .new-level {
    font-size: 1.5rem;
  }

  .continue-button {
    width: calc(100% - 48px);
    margin: 0 24px 24px;
  }
}
</style>
