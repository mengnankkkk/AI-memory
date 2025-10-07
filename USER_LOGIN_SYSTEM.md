# 用户登录系统实现文档

## ✅ 后端已完成

### 1. 数据库模型
- `app/models/user.py` - User模型（用户表）
- 字段：id, username, email, hashed_password, is_active, created_at, updated_at

### 2. 认证工具
- `app/core/auth.py` - JWT工具
  - `verify_password()` - 验证密码
  - `get_password_hash()` - 生成密码哈希
  - `create_access_token()` - 创建JWT token
  - `decode_access_token()` - 解码JWT token

### 3. API端点
- `app/api/auth.py`
  - `POST /api/auth/register` - 用户注册
  - `POST /api/auth/login` - 用户登录
  - `GET /api/auth/me` - 获取当前用户信息
  - `POST /api/auth/logout` - 用户登出

- `app/api/companions.py` (已更新为需要认证)
  - `GET /api/companions/` - 获取当前用户的所有角色（需认证）
  - `POST /api/companions/` - 创建新角色（需认证）
  - `GET /api/companions/{id}` - 获取角色详情（需认证）
  - `DELETE /api/companions/{id}` - 删除角色（需认证）

### 4. 配置
- SECRET_KEY已添加到`app/core/config.py`
- User模型已添加到数据库初始化

### 5. 依赖项
已添加到`requirements.txt`:
- `python-jose[cryptography]` - JWT处理
- `passlib[bcrypt]` - 密码哈希
- `pydantic[email]` - 邮箱验证

---

## 🚀 前端实现指南

### 第一步：安装依赖

```bash
cd frontend
npm install axios
```

### 第二步：创建API服务

创建 `frontend/src/services/auth.ts`:

```typescript
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 自动添加token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 处理401错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效，清除本地存储并跳转登录
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
}

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// 认证API
export const authAPI = {
  // 登录
  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', data)
    return response.data
  },

  // 注册
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  // 获取当前用户
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me')
    return response.data
  },

  // 登出
  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  },
}

// 导出api实例供其他服务使用
export default api
```

### 第三步：创建状态管理 (Pinia)

创建 `frontend/src/stores/auth.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI, type User } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)

  // 从localStorage恢复状态
  const init = () => {
    const savedToken = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user')

    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }

  // 登录
  const login = async (username: string, password: string) => {
    try {
      const response = await authAPI.login({ username, password })

      token.value = response.access_token
      user.value = response.user

      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '登录失败',
      }
    }
  }

  // 注册
  const register = async (
    username: string,
    email: string,
    password: string
  ) => {
    try {
      const response = await authAPI.register({ username, email, password })

      token.value = response.access_token
      user.value = response.user

      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '注册失败',
      }
    }
  }

  // 登出
  const logout = async () => {
    try {
      await authAPI.logout()
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    }
  }

  // 刷新用户信息
  const refreshUser = async () => {
    try {
      user.value = await authAPI.getCurrentUser()
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (error) {
      // Token无效，清除状态
      logout()
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    init,
    login,
    register,
    logout,
    refreshUser,
  }
})
```

### 第四步：创建登录页面

创建 `frontend/src/views/Login.vue`:

```vue
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
```

### 第五步：更新路由

修改 `frontend/src/router/index.ts`:

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: true },
    },
    // 其他路由...
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 初始化auth store（从localStorage恢复状态）
  if (!authStore.token) {
    authStore.init()
  }

  const requiresAuth = to.meta.requiresAuth !== false // 默认需要认证

  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未登录，跳转到登录页
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    // 已登录用户访问登录页，跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router
```

### 第六步：更新App.vue

修改 `frontend/src/App.vue`，在应用初始化时恢复用户状态：

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // 从localStorage恢复用户状态
  authStore.init()
})
</script>
```

---

## 🎯 使用流程

### 1. 启动后端

```bash
cd backend

# 安装新依赖
pip install -r requirements.txt

# 删除旧数据库（重建）
rm ai_companion.db

# 启动服务
uvicorn app.main:app --reload
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 测试流程

1. 访问 `http://localhost:5173`
2. 自动跳转到登录页 `/login`
3. 点击"立即注册"，创建账号
4. 注册成功后自动登录并跳转到首页
5. 在首页创建角色
6. 角色会自动关联到当前登录用户
7. 刷新页面，登录状态会保持（通过localStorage）
8. 点击登出，清除状态并跳转到登录页

---

## ✨ 特性

- ✅ JWT认证（7天有效期）
- ✅ 密码加密存储（bcrypt）
- ✅ 自动token刷新和错误处理
- ✅ 用户角色持久化
- ✅ 登录状态保持（localStorage）
- ✅ 路由守卫（未登录自动跳转）
- ✅ 美观的登录/注册页面

---

## 📝 API示例

### 注册

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "test@example.com",
    "password": "123456"
  }'
```

### 登录

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "password": "123456"
  }'
```

### 获取用户角色（需要token）

```bash
curl -X GET "http://localhost:8000/api/companions/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

完成！🎉
