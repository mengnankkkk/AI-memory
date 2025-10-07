<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">{{ isRegisterMode ? '注册账号' : '登录' }}</h1>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            placeholder="请输入用户名"
            :disabled="loading"
          />
        </div>

        <div v-if="isRegisterMode" class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            placeholder="请输入邮箱"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            :placeholder="isRegisterMode ? '请输入密码（至少6位）' : '请输入密码'"
            :disabled="loading"
          />
        </div>

        <div v-if="isRegisterMode" class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            required
            placeholder="请再次输入密码"
            :disabled="loading"
          />
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? '处理中...' : isRegisterMode ? '注册' : '登录' }}
        </button>

        <div class="switch-mode">
          <span v-if="isRegisterMode">
            已有账号？
            <a href="#" @click.prevent="toggleMode">立即登录</a>
          </span>
          <span v-else>
            还没有账号？
            <a href="#" @click.prevent="toggleMode">立即注册</a>
          </span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isRegisterMode = ref(false)
const loading = ref(false)
const errorMessage = ref('')

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  errorMessage.value = ''
  form.value = {
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  }
}

const handleSubmit = async () => {
  errorMessage.value = ''

  // 表单验证
  if (isRegisterMode.value) {
    if (form.value.password.length < 6) {
      errorMessage.value = '密码至少需要6位'
      return
    }
    if (form.value.password !== form.value.confirmPassword) {
      errorMessage.value = '两次输入的密码不一致'
      return
    }
  }

  loading.value = true

  try {
    let result
    if (isRegisterMode.value) {
      result = await authStore.register(
        form.value.username,
        form.value.email,
        form.value.password
      )
    } else {
      result = await authStore.login(form.value.username, form.value.password)
    }

    if (result.success) {
      router.push('/')
    } else {
      errorMessage.value = result.message || '操作失败'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 28px;
  font-weight: 600;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #555;
  font-size: 14px;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  color: #f44336;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background-color: #ffebee;
  border-radius: 8px;
}

.submit-button {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.switch-mode {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.switch-mode a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.switch-mode a:hover {
  text-decoration: underline;
}
</style>
