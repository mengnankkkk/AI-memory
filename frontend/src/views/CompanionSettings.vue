<template>
  <div class="max-w-xl mx-auto p-6">
    <h2 class="text-2xl font-bold mb-4">伙伴设置</h2>
    <form @submit.prevent="onSave">
      <div class="mb-4">
        <label class="block mb-1 font-medium">名称</label>
        <input v-model="form.name" class="input input-bordered w-full" required />
      </div>
      <div class="mb-4">
        <label class="block mb-1 font-medium">头像</label>
        <select v-model="form.avatarId" class="select select-bordered w-full">
          <option v-for="avatar in avatars" :key="avatar.id" :value="avatar.id">
            {{ avatar.name }}
          </option>
        </select>
      </div>
      <div class="mb-4">
        <label class="block mb-1 font-medium">性格原型</label>
        <select v-model="form.personalityArchetype" class="select select-bordered w-full">
          <option value="listener">倾听者</option>
          <option value="cheerleader">鼓励者</option>
          <option value="analyst">分析者</option>
        </select>
      </div>
      <div class="mb-4">
        <label class="block mb-1 font-medium">自定义系统提示词（可选）</label>
        <textarea v-model="form.customPrompt" class="textarea textarea-bordered w-full" rows="3" placeholder="不填写则使用默认提示词"></textarea>
      </div>
      <div class="flex gap-2 mt-6">
        <button type="submit" class="btn btn-primary">保存</button>
        <button type="button" class="btn btn-warning" @click="onReset">重置伙伴</button>
        <button type="button" class="btn btn-error" @click="onDelete">删除伙伴</button>
      </div>
    </form>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { companionService } from '@/services/companion'
import type { Companion } from '@/types'

const router = useRouter()
const route = useRoute()
const companionId = Number(route.params.companionId)

const form = ref({
  name: '',
  avatarId: '',
  personalityArchetype: 'listener',
  customPrompt: ''
})

const avatars = [
  { id: 'avatar1', name: '头像1' },
  { id: 'avatar2', name: '头像2' },
  { id: 'avatar3', name: '头像3' }
]

async function loadCompanion() {
  try {
    const data = await companionService.get(companionId)
    form.value.name = data.name
    form.value.avatarId = data.avatar_id
    form.value.personalityArchetype = data.personality_archetype
    form.value.customPrompt = data.custom_greeting || ''
  } catch (e) {
    alert('加载伙伴信息失败')
  }
}

onMounted(() => {
  loadCompanion()
})

async function onSave() {
  try {
    await companionService.update(companionId, {
      name: form.value.name,
      avatar_id: form.value.avatarId,
      personality_archetype: form.value.personalityArchetype,
      custom_greeting: form.value.customPrompt
    })
    alert('保存成功')
    router.push({ name: 'chat', params: { companionId } })
  } catch (e) {
    alert('保存失败')
  }
}

async function onReset() {
  if (confirm('确定要重置伙伴配置吗？')) {
    try {
      await companionService.reset(companionId)
      await loadCompanion()
      alert('已重置')
    } catch (e) {
      alert('重置失败')
    }
  }
}

async function onDelete() {
  if (confirm('确定要删除该伙伴吗？此操作不可恢复！')) {
    try {
      await companionService.delete(companionId)
      alert('已删除')
      router.push({ name: 'home' })
    } catch (e) {
      alert('删除失败')
    }
  }
}
</script>

<style scoped>
.input, .select, .textarea {
  @apply border rounded px-3 py-2;
}
.btn {
  @apply px-4 py-2 rounded font-medium;
}
</style>
