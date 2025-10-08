import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'

console.log('🚀 main.ts 开始执行')

const app = createApp(App)
console.log('✅ Vue 应用创建成功')

const pinia = createPinia()
console.log('✅ Pinia 创建成功')

app.use(pinia)
app.use(router)
console.log('✅ 插件注册成功')

// 初始化认证状态
const authStore = useAuthStore()
authStore.init()
console.log('✅ 认证状态初始化完成')

app.mount('#app')
console.log('✅ Vue 应用挂载完成')
