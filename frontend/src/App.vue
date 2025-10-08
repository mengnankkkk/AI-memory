<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'

console.log('🎯 App.vue 组件开始渲染')

onMounted(() => {
  console.log('✅ App.vue 组件已挂载')
})
</script>

<template>
  <div>
    <p>App.vue 正在渲染...</p>
    <RouterView />
  </div>
</template>

<style scoped>
</style>
