<template>
  <div v-if="count > 0" class="task-badge" :class="{ urgent: isUrgent }">
    <span class="badge-count">{{ count }}</span>
    <span v-if="isUrgent" class="badge-pulse"></span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  count: number
  isUrgent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isUrgent: false
})
</script>

<style scoped>
.task-badge {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 6px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.4);
}

.task-badge.urgent {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.badge-count {
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  line-height: 1;
}

.badge-pulse {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 12px;
  border: 2px solid #f59e0b;
  animation: pulsate 2s ease-out infinite;
}

@keyframes pulsate {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}
</style>
