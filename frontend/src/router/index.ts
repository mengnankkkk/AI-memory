import { createRouter, createWebHistory } from 'vue-router'
import CreateCompanion from '@/views/CreateCompanion.vue'
import Chat from '@/views/Chat.vue'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/create',
      name: 'create',
      component: CreateCompanion
    },
    {
      path: '/chat/:companionId',
      name: 'chat',
      component: Chat,
      props: true
    }
  ]
})

export default router
