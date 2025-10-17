<template>
  <Transition name="feedback">
    <div v-if="visible" class="gift-feedback-overlay" @click="close">
      <div class="gift-feedback-card" @click.stop>
        <!-- 礼物图标动画 -->
        <div class="gift-animation">
          <div class="gift-icon-wrapper">
            <span class="gift-emoji">{{ giftEmoji }}</span>
            <div class="sparkles">
              <span v-for="i in 8" :key="i" class="sparkle" :style="getSparkleStyle(i)">✨</span>
            </div>
          </div>
        </div>

        <!-- 伙伴反应 -->
        <div class="companion-reaction">
          <div class="reaction-bubble">
            <p class="reaction-text">{{ companionReaction }}</p>
          </div>
        </div>

        <!-- 好感度变动 -->
        <div class="affinity-change">
          <div class="affinity-label">好感度</div>
          <div class="affinity-value" :class="affinityChangeClass">
            <span class="change-amount">{{ affinityChangeText }}</span>
            <div class="progress-animation">
              <div class="old-value">{{ oldAffinity }}</div>
              <div class="arrow">→</div>
              <div class="new-value">{{ newAffinity }}</div>
            </div>
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
import { ref, computed, watch } from 'vue'

interface Props {
  visible: boolean
  giftEmoji: string
  giftName: string
  companionReaction: string
  affinityChange: number
  oldAffinity: number
  newAffinity: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const affinityChangeText = computed(() => {
  const change = props.affinityChange
  return change > 0 ? `+${change}` : `${change}`
})

const affinityChangeClass = computed(() => {
  return props.affinityChange > 0 ? 'positive' : 'negative'
})

const close = () => {
  emit('close')
}

// 自动关闭
watch(() => props.visible, (newVal) => {
  if (newVal) {
    setTimeout(() => {
      close()
    }, 4000) // 4秒后自动关闭
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
  const hue = Math.random() * 360

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
.gift-feedback-overlay {
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

.gift-feedback-card {
  position: relative;
  background: linear-gradient(135deg, #fff5f7 0%, #fff 100%);
  border-radius: 24px;
  padding: 40px;
  max-width: 500px;
  width: 100%;
  box-shadow:
    0 20px 60px rgba(255, 105, 180, 0.3),
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

/* 礼物动画 */
.gift-animation {
  text-align: center;
  margin-bottom: 24px;
}

.gift-icon-wrapper {
  position: relative;
  display: inline-block;
}

.gift-emoji {
  font-size: 5rem;
  display: inline-block;
  animation: giftBounce 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes giftBounce {
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

/* 伙伴反应 */
.companion-reaction {
  margin-bottom: 32px;
}

.reaction-bubble {
  background: linear-gradient(135deg, #f9a8d4 0%, #f472b6 100%);
  border-radius: 20px;
  padding: 20px 24px;
  position: relative;
  box-shadow: 0 8px 24px rgba(244, 114, 182, 0.3);
  animation: bubbleEnter 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s backwards;
}

@keyframes bubbleEnter {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.reaction-text {
  margin: 0;
  color: white;
  font-size: 1.125rem;
  line-height: 1.6;
  text-align: center;
  font-weight: 500;
}

/* 好感度变动 */
.affinity-change {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  animation: affinityEnter 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.4s backwards;
}

@keyframes affinityEnter {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.affinity-label {
  text-align: center;
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.affinity-value {
  text-align: center;
}

.change-amount {
  display: inline-block;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 16px;
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

.affinity-value.positive .change-amount {
  color: #10b981;
  text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.affinity-value.negative .change-amount {
  color: #ef4444;
  text-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
}

.progress-animation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 1.125rem;
  color: #374151;
  animation: progressSlide 0.6s ease-out 0.8s backwards;
}

@keyframes progressSlide {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.old-value {
  opacity: 0.5;
  font-weight: 500;
}

.arrow {
  color: #9ca3af;
  font-size: 1.5rem;
}

.new-value {
  font-weight: 700;
  color: #f472b6;
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
  background: hsl(var(--hue, 340), 70%, 60%);
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

.feedback-enter-active .gift-feedback-card {
  animation: cardEnter 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.feedback-leave-active .gift-feedback-card {
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
  .gift-feedback-card {
    padding: 32px 24px;
  }

  .gift-emoji {
    font-size: 4rem;
  }

  .reaction-text {
    font-size: 1rem;
  }

  .change-amount {
    font-size: 2rem;
  }

  .progress-animation {
    font-size: 1rem;
  }
}
</style>
