<template>
  <Transition name="modal">
    <div v-if="show" class="modal-overlay" @click="handleClose">
      <div class="modal-container" @click.stop>
        <!-- 庆祝背景效果 -->
        <div class="celebration-bg">
          <div v-for="i in 20" :key="i"
            class="confetti"
            :style="{
              left: Math.random() * 100 + '%',
              animationDelay: Math.random() * 2 + 's',
              background: getRandomColor()
            }"
          ></div>
        </div>

        <!-- 主内容 -->
        <div class="modal-content">
          <!-- 等级图标 -->
          <div class="level-icon-container">
            <div class="level-icon" :style="{ color: levelConfig?.color }">
              {{ levelConfig?.icon }}
            </div>
            <div class="star-burst">
              <span v-for="i in 8" :key="i" class="star" :style="{ transform: `rotate(${i * 45}deg)` }">
                ⭐
              </span>
            </div>
          </div>

          <!-- 标题 -->
          <h2 class="modal-title" :style="{ color: levelConfig?.color }">
            🎉 关系升级！🎉
          </h2>

          <!-- 等级信息 -->
          <div class="level-info">
            <div class="level-badge" :style="{
              background: levelConfig?.bgColor,
              color: levelConfig?.color,
              borderColor: levelConfig?.color
            }">
              {{ levelConfig?.name }}
            </div>
            <p class="level-description">{{ levelConfig?.description }}</p>
          </div>

          <!-- 好感度进度 -->
          <div class="affinity-progress">
            <div class="progress-label">
              <span>好感度</span>
              <span class="font-bold">{{ affinityScore }}/1000</span>
            </div>
            <div class="progress-bar-container">
              <div
                class="progress-bar-fill"
                :style="{
                  width: (affinityScore / 1000 * 100) + '%',
                  background: `linear-gradient(90deg, ${levelConfig?.color}, ${levelConfig?.bgColor})`
                }"
              >
                <div class="progress-shine"></div>
              </div>
            </div>
          </div>

          <!-- 消息 -->
          <p class="companion-message" v-if="message">
            "{{ message }}"
          </p>

          <!-- 关闭按钮 -->
          <button
            @click="handleClose"
            class="close-button"
            :style="{
              background: `linear-gradient(135deg, ${levelConfig?.color}, ${levelConfig?.bgColor})`,
              boxShadow: `0 4px 12px ${levelConfig?.color}40`
            }"
          >
            太好了！
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AffinityLevelConfig } from '@/config/affinity-config'

interface Props {
  show: boolean
  levelKey: string
  levelConfig: AffinityLevelConfig | null
  affinityScore: number
  companionName?: string
  message?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const handleClose = () => {
  emit('close')
}

const getRandomColor = () => {
  const colors = [
    '#FF6B9D', '#C44569', '#FFA06B', '#FFCB6B',
    '#95E1D3', '#6BCF7F', '#4ECDC4', '#B4A7D6',
    '#AA96DA', '#FCBAD3'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}
</script>

<style scoped>
/* 模态框过渡效果 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.8) translateY(-20px);
}

/* 模态框覆盖层 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

/* 模态框容器 */
.modal-container {
  position: relative;
  max-width: 500px;
  width: 100%;
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

/* 庆祝背景 */
.celebration-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

/* 五彩纸屑 */
.confetti {
  position: absolute;
  width: 10px;
  height: 10px;
  top: -20px;
  animation: confettiFall 3s ease-in-out infinite;
  opacity: 0.8;
}

@keyframes confettiFall {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) rotate(720deg);
    opacity: 0;
  }
}

/* 主内容 */
.modal-content {
  position: relative;
  padding: 40px 30px;
  text-align: center;
  z-index: 1;
}

/* 等级图标容器 */
.level-icon-container {
  position: relative;
  margin: 0 auto 30px;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 等级图标 */
.level-icon {
  font-size: 80px;
  animation: iconBounce 0.6s ease-in-out;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.2));
}

@keyframes iconBounce {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.3);
  }
}

/* 星星爆发效果 */
.star-burst {
  position: absolute;
  width: 100%;
  height: 100%;
  animation: rotateStar 3s linear infinite;
}

.star {
  position: absolute;
  top: 50%;
  left: 50%;
  font-size: 20px;
  animation: starPulse 1.5s ease-in-out infinite;
}

@keyframes rotateStar {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes starPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 1;
  }
}

/* 标题 */
.modal-title {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 20px;
  animation: titleShake 0.5s ease-in-out;
}

@keyframes titleShake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-10px);
  }
  75% {
    transform: translateX(10px);
  }
}

/* 等级信息 */
.level-info {
  margin-bottom: 30px;
}

.level-badge {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 50px;
  font-size: 24px;
  font-weight: bold;
  border: 3px solid;
  margin-bottom: 12px;
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.level-description {
  color: #666;
  font-size: 16px;
}

/* 好感度进度 */
.affinity-progress {
  margin: 30px 0;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.progress-bar-container {
  height: 12px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-bar-fill {
  height: 100%;
  border-radius: 10px;
  position: relative;
  transition: width 1s ease-out;
  animation: progressGlow 2s ease-in-out infinite;
}

@keyframes progressGlow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.8);
  }
}

.progress-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
  animation: shine 2s ease-in-out infinite;
}

@keyframes shine {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

/* 伙伴消息 */
.companion-message {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  border-radius: 16px;
  font-size: 16px;
  font-style: italic;
  color: #333;
  margin: 20px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 关闭按钮 */
.close-button {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.close-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.close-button:active {
  transform: translateY(0);
}
</style>
