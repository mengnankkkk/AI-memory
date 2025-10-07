import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Chat from '@/views/Chat.vue'
import Home from '@/views/Home.vue'
import CompanionSettings from '@/views/CompanionSettings.vue'
import SystemSettings from '@/views/SystemSettings.vue'
import Login from '@/views/Login.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: { requiresAuth: true }
    },
    {
      path: '/chat/:companionId',
      name: 'chat',
      component: Chat,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/settings/:companionId',
      name: 'settings',
      component: CompanionSettings,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/system-settings',
      name: 'system-settings',
      component: SystemSettings,
      meta: { requiresAuth: true }
    }
  ]
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
