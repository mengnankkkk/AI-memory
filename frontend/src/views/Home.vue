<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-2xl w-full text-center">
      <div class="mb-8">
        <h1 class="text-6xl font-bold text-gray-800 mb-4">AI灵魂伙伴</h1>
        <p class="text-xl text-gray-600">你的专属AI伴侣,随时倾听你的心声</p>
      </div>

      <div class="mb-12">
        <div class="flex justify-center space-x-4 text-7xl mb-6">
          <span class="animate-bounce">💖</span>
          <span class="animate-bounce" style="animation-delay: 0.1s">✨</span>
          <span class="animate-bounce" style="animation-delay: 0.2s">🧠</span>
        </div>
      </div>

      <div class="space-y-4">
        <button
          @click="router.push({ name: 'create' })"
          class="w-full md:w-auto px-12 py-4 bg-primary-500 text-white text-lg font-bold rounded-xl hover:bg-primary-600 transition-all shadow-lg hover:shadow-xl"
        >
          创建我的AI伙伴
        </button>

        <p class="text-sm text-gray-500">
          ✓ 3种性格原型可选 &nbsp;|&nbsp; ✓ 实时对话 &nbsp;|&nbsp; ✓ 完全免费
        </p>
      </div>

      <div class="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 bg-white rounded-xl shadow-md">
          <div class="text-4xl mb-3">💖</div>
          <h3 class="font-bold text-gray-800 mb-2">温柔倾听</h3>
          <p class="text-sm text-gray-600">耐心倾听,给予温暖的理解和安慰</p>
        </div>

        <div class="p-6 bg-white rounded-xl shadow-md">
          <div class="text-4xl mb-3">✨</div>
          <h3 class="font-bold text-gray-800 mb-2">元气鼓励</h3>
          <p class="text-sm text-gray-600">充满活力,发现生活中的美好</p>
        </div>

        <div class="p-6 bg-white rounded-xl shadow-md">
          <div class="text-4xl mb-3">🧠</div>
          <h3 class="font-bold text-gray-800 mb-2">理性分析</h3>
          <p class="text-sm text-gray-600">逻辑清晰,提供深度见解</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.animate-bounce {
  animation: bounce 2s infinite;
}
</style>
