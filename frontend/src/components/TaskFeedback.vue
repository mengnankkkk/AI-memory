<template>
  <Transition name="feedback">
    <div v-if="visible" class="task-feedback-overlay" @click="close">
      <div class="task-feedback-card" @click.stop>
        <!-- 任务图标动画 -->
        <div class="task-animation">
          <div class="task-icon-wrapper">
            <span class="task-icon">{{ taskIcon }}</span>
            <div class="sparkles">
              <span v-for="i in 8" :key="i" class="sparkle" :style="getSparkleStyle(i)">✨</span>
            </div>
          </div>
        </div>

        <!-- 完成标题 -->
        <div class="completion-header">
          <h3>任务完成！</h3>
          <p class="task-description">{{ taskDescription }}</p>
        </div>

        <!-- 奖励显示 -->
        <div class="reward-display">
          <div class="reward-label">获得奖励</div>
          <div class="reward-value">
            <span class="reward-amount">+{{ reward }}</span>
            <span class="reward-type">好感度</span>
          </div>
        </div>

        <!-- 关闭按钮 -->
        <button class="close-button" @click="close">
          <i class="fas fa-times"></i>
        </button>

        <!-- 粒子效果 -->
        <div class="particles">
          <div v-for="i in 20" :key="i" class="particle" :style="getParticleStyle(i)"></div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'

interface Props {
  visible: boolean
  taskIcon: string
  taskDescription: string
  reward: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const close = () => {
  emit('close')
}

// 自动关闭
watch(() => props.visible, (newVal) => {
  if (newVal) {
    setTimeout(() => {
      close()
    }, 3000) // 3秒后自动关闭
  }
})

// 星星闪烁样式
const getSparkleStyle = (index: number) => {
  const angle = (index / 8) * 360
  const distance = 60
  const x = Math.cos((angle * Math.PI) / 180) * distance
  const y = Math.sin((angle * Math.PI) / 180) * distance
  return {
    transform: `translate(${x}px, ${y}px)`,
    animationDelay: `${index * 0.1}s`
  }
}

// 粒子效果样式
const getParticleStyle = (index: number) => {
  const angle = (index / 20) * 360
  const distance = Math.random() * 150 + 100
  const x = Math.cos((angle * Math.PI) / 180) * distance
  const y = Math.sin((angle * Math.PI) / 180) * distance
  const hue = Math.random() * 60 + 30 // 金黄色调

  return {
    left: '50%',
    top: '50%',
    '--tx': `${x}px`,
    '--ty': `${y}px`,
    '--hue': hue,
    animationDelay: `${index * 0.05}s`,
    animationDuration: `${0.8 + Math.random() * 0.4}s`
  }
}
</script>

<style scoped>
.task-feedback-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.task-feedback-card {
  position: relative;
  background: linear-gradient(135deg, #fffbf0 0%, #fff 100%);
  border-radius: 24px;
  padding: 40px;
  max-width: 500px;
  width: 100%;
  box-shadow:
    0 20px 60px rgba(251, 191, 36, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.8);
  animation: cardEnter 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(30px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 任务动画 */
.task-animation {
  text-align: center;
  margin-bottom: 24px;
}

.task-icon-wrapper {
  position: relative;
  display: inline-block;
}

.task-icon {
  font-size: 5rem;
  display: inline-block;
  animation: taskBounce 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes taskBounce {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-20px) scale(1.2);
  }
}

.sparkles {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
}

.sparkle {
  position: absolute;
  font-size: 1.5rem;
  animation: sparkleFloat 1.5s ease-out infinite;
  opacity: 0;
}

@keyframes sparkleFloat {
  0% {
    opacity: 0;
    transform: translate(0, 0) scale(0);
  }
  50% {
    opacity: 1;
    transform: translate(var(--tx, 0), var(--ty, 0)) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(var(--tx, 0), var(--ty, 0)) scale(0);
  }
}

/* 完成标题 */
.completion-header {
  text-align: center;
  margin-bottom: 32px;
}

.completion-header h3 {
  margin: 0 0 8px 0;
  color: #f59e0b;
  font-size: 1.75rem;
  font-weight: 700;
  animation: titleFade 0.5s ease-out 0.2s backwards;
}

@keyframes titleFade {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.task-description {
  margin: 0;
  color: #6b7280;
  font-size: 1.125rem;
  animation: descriptionFade 0.5s ease-out 0.3s backwards;
}

@keyframes descriptionFade {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 奖励显示 */
.reward-display {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  animation: rewardEnter 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.4s backwards;
}

@keyframes rewardEnter {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.reward-label {
  text-align: center;
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.reward-value {
  text-align: center;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
}

.reward-amount {
  font-size: 2.5rem;
  font-weight: 700;
  color: #10b981;
  text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
  animation: numberPop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.6s backwards;
}

@keyframes numberPop {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.reward-type {
  font-size: 1.125rem;
  color: #374151;
  font-weight: 500;
}

/* 关闭按钮 */
.close-button {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  font-size: 1.125rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.close-button:hover {
  background: white;
  color: #374151;
  transform: scale(1.1);
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
  border-radius: 24px;
}

.particle {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: hsl(var(--hue, 45), 90%, 60%);
  animation: particleFloat 1s ease-out forwards;
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

/* 过渡动画 */
.feedback-enter-active,
.feedback-leave-active {
  transition: opacity 0.3s ease;
}

.feedback-enter-from,
.feedback-leave-to {
  opacity: 0;
}

.feedback-enter-active .task-feedback-card {
  animation: cardEnter 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.feedback-leave-active .task-feedback-card {
  animation: cardLeave 0.3s ease;
}

@keyframes cardLeave {
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
  .task-feedback-card {
    padding: 32px 24px;
  }

  .task-icon {
    font-size: 4rem;
  }

  .completion-header h3 {
    font-size: 1.5rem;
  }

  .task-description {
    font-size: 1rem;
  }

  .reward-amount {
    font-size: 2rem;
  }
}
</style>
