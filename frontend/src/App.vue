<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // 从localStorage恢复用户状态
  authStore.init()
})
</script>

<template>
  <RouterView />
</template>

<style scoped>
</style>
