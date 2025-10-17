<template>
  <div class="task-progress-bar">
    <div class="progress-info">
      <span class="progress-label">{{ currentProgress }}/{{ maxProgress }}</span>
      <span class="progress-percentage">{{ percentage }}%</span>
    </div>
    <div class="progress-track">
      <div
        class="progress-fill"
        :style="{ width: percentage + '%' }"
        :class="progressClass"
      >
        <!-- 里程碑标记 -->
        <div
          v-for="(milestone, index) in milestones"
          :key="index"
          class="milestone-marker"
          :style="{ left: (milestone.progress / maxProgress * 100) + '%' }"
          :class="{ active: currentProgress >= milestone.progress }"
        >
          <div class="milestone-dot"></div>
          <div class="milestone-tooltip">+{{ milestone.bonus }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Milestone {
  progress: number
  bonus: number
}

interface Props {
  currentProgress: number
  maxProgress: number
  milestones?: Milestone[]
}

const props = withDefaults(defineProps<Props>(), {
  milestones: () => []
})

const percentage = computed(() => {
  if (props.maxProgress === 0) return 0
  return Math.min(Math.round((props.currentProgress / props.maxProgress) * 100), 100)
})

const progressClass = computed(() => {
  const pct = percentage.value
  if (pct < 25) return 'progress-low'
  if (pct < 50) return 'progress-medium-low'
  if (pct < 75) return 'progress-medium-high'
  return 'progress-high'
})
</script>

<style scoped>
.task-progress-bar {
  margin-top: 8px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.progress-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 600;
}

.progress-percentage {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 700;
}

.progress-track {
  position: relative;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: visible;
}

.progress-fill {
  position: relative;
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease, background 0.3s ease;
}

.progress-low {
  background: linear-gradient(90deg, #fca5a5, #f87171);
}

.progress-medium-low {
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
}

.progress-medium-high {
  background: linear-gradient(90deg, #60a5fa, #3b82f6);
}

.progress-high {
  background: linear-gradient(90deg, #34d399, #10b981);
}

.milestone-marker {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
}

.milestone-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: white;
  border: 2px solid #d1d5db;
  transition: all 0.3s ease;
}

.milestone-marker.active .milestone-dot {
  background: #fbbf24;
  border-color: #f59e0b;
  box-shadow: 0 0 8px rgba(251, 191, 36, 0.6);
  animation: milestonePulse 1s ease-in-out;
}

@keyframes milestonePulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.3);
  }
}

.milestone-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 6px;
  padding: 2px 6px;
  background: #fbbf24;
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 4px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.milestone-marker:hover .milestone-tooltip,
.milestone-marker.active .milestone-tooltip {
  opacity: 1;
}
</style>
