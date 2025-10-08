import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Chat from '@/views/Chat.vue'
import Home from '@/views/Home.vue'
import CompanionSettings from '@/views/CompanionSettings.vue'
import SystemSettings from '@/views/SystemSettings.vue'
import Login from '@/views/Login.vue'
import CreateCompanion from '@/views/CreateCompanion.vue'

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
    },
    {
      path: '/create-companion',
      name: 'create-companion',
      component: CreateCompanion,
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  const requiresAuth = to.meta.requiresAuth !== false // 默认需要认证
  
  // 调试信息
  console.log('路由守卫:', {
    to: to.path,
    requiresAuth,
    isAuthenticated: authStore.isAuthenticated,
    hasToken: !!authStore.token,
    hasUser: !!authStore.user
  })

  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未登录，跳转到登录页
    console.log('需要认证但未登录，跳转到登录页')
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    // 已登录用户访问登录页，跳转到首页
    console.log('已登录用户访问登录页，跳转到首页')
    next('/')
  } else {
    console.log('允许访问:', to.path)
    next()
  }
})

export default router
