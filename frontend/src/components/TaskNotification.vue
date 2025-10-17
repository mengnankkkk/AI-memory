<template>
  <Transition name="notification">
    <div v-if="visible" class="task-notification">
      <div class="notification-header">
        <div class="notification-icon">📋</div>
        <h4>新的每日任务！</h4>
        <button class="close-btn" @click="close">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="task-summary">
        <div class="summary-item">
          <span class="summary-label">今日任务</span>
          <span class="summary-value">{{ totalTasks }}个</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">总奖励</span>
          <span class="summary-value highlight">+{{ totalReward }}好感度</span>
        </div>
      </div>

      <div class="task-preview">
        <div v-for="task in tasks.slice(0, 3)" :key="task.task_id" class="preview-task">
          <i :class="getTaskIcon(task.task_type)"></i>
          <span>{{ task.description }}</span>
          <span class="task-reward">+{{ task.reward_affinity }}</span>
        </div>
      </div>

      <div class="notification-actions">
        <button class="action-btn primary" @click="goToTasks">
          立即查看
        </button>
        <button class="action-btn secondary" @click="close">
          稍后再说
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DailyTaskResponse } from '@/types/romance'

interface Props {
  visible: boolean
  tasks: DailyTaskResponse[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  goToTasks: []
}>()

const totalTasks = computed(() => props.tasks.length)
const totalReward = computed(() =>
  props.tasks.reduce((sum, task) => sum + task.reward_affinity, 0)
)

const close = () => {
  emit('close')
}

const goToTasks = () => {
  emit('goToTasks')
  close()
}

const getTaskIcon = (taskType: string): string => {
  const iconMap: Record<string, string> = {
    'chat': 'fas fa-comments',
    'compliment': 'fas fa-heart',
    'romantic': 'fas fa-kiss-wink-heart',
    'gift': 'fas fa-gift'
  }
  return iconMap[taskType] || 'fas fa-star'
}
</script>

<style scoped>
.task-notification {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border-radius: 20px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  z-index: 10001;
  border: 2px solid #10b981;
}

.notification-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.notification-icon {
  font-size: 2rem;
  animation: iconBounce 0.6s ease-out;
}

@keyframes iconBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.notification-header h4 {
  flex: 1;
  margin: 0;
  color: #374151;
  font-size: 1.25rem;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: #f3f4f6;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.task-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.summary-item {
  background: white;
  padding: 12px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.summary-label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 4px;
}

.summary-value {
  display: block;
  font-size: 1.125rem;
  font-weight: 700;
  color: #374151;
}

.summary-value.highlight {
  color: #10b981;
}

.task-preview {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.preview-task {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 0.875rem;
  color: #374151;
}

.preview-task:not(:last-child) {
  border-bottom: 1px solid #e5e7eb;
}

.preview-task i {
  color: #10b981;
  width: 20px;
}

.preview-task span:nth-child(2) {
  flex: 1;
}

.task-reward {
  color: #10b981;
  font-weight: 600;
  font-size: 0.75rem;
}

.notification-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-btn {
  padding: 12px;
  border-radius: 12px;
  border: none;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.primary {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.action-btn.secondary {
  background: white;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}

.action-btn.secondary:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

/* 过渡动画 */
.notification-enter-active {
  animation: slideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.notification-leave-active {
  animation: slideOut 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

@keyframes slideOut {
  from {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
  to {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.9);
  }
}

/* 响应式 */
@media (max-width: 480px) {
  .task-notification {
    width: 95%;
    padding: 20px;
  }

  .notification-actions {
    grid-template-columns: 1fr;
  }
}
</style>
