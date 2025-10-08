/**
 * WebSocket聊天服务
 * 使用Socket.IO实现实时流式聊天
 */
import { io, Socket } from 'socket.io-client'
import { ref, computed } from 'vue'

interface ChatMessage {
  id?: number
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

interface StreamingMessage {
  id: string
  content: string
  isComplete: boolean
}

export const useWebSocketChat = () => {
  const socket = ref<Socket | null>(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const currentStreamingMessage = ref<StreamingMessage | null>(null)
  const autoJoinCallback = ref<(() => void) | null>(null)
  
  // 连接到WebSocket服务器
  const connect = () => {
    if (socket.value?.connected) return
    
    isConnecting.value = true
    
    socket.value = io('http://localhost:8000', {
      transports: ['websocket', 'polling'],
      timeout: 10000,
      forceNew: true,
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    })
    
    // 连接事件
    socket.value.on('connect', () => {
      console.log('✅ WebSocket连接成功')
      isConnected.value = true
      isConnecting.value = false
      
      // 如果有自动加入回调，执行它
      if (autoJoinCallback.value) {
        setTimeout(() => {
          autoJoinCallback.value?.()
        }, 500)
      }
    })
    
    socket.value.on('disconnect', () => {
      console.log('❌ WebSocket连接断开')
      isConnected.value = false
      isConnecting.value = false
    })
    
    socket.value.on('connect_error', (error) => {
      console.error('❌ WebSocket连接错误:', error)
      isConnected.value = false
      isConnecting.value = false
    })
    
    return socket.value
  }
  
  // 断开连接
  const disconnect = () => {
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
      isConnected.value = false
      isConnecting.value = false
    }
  }
  
  // 加入聊天房间
  const joinChat = (companionId: number, userId: string, chatSessionId?: number) => {
    if (!socket.value?.connected) return
    
    socket.value.emit('join_chat', {
      companion_id: companionId,
      user_id: userId,
      chat_session_id: chatSessionId
    })
  }
  
  // 发送消息
  const sendMessage = (message: string, sessionId?: number) => {
    if (!socket.value?.connected) return
    
    console.log('🔍 WebSocket发送消息:', {
      message,
      sessionId,
      connected: socket.value?.connected
    })
    
    socket.value.emit('send_message', {
      message: message,
      session_id: sessionId
    })
  }
  
  // 监听消息事件
  const onMessageReceived = (callback: (message: ChatMessage) => void) => {
    if (!socket.value) return
    
    socket.value.on('message_received', callback)
  }
  
  // 监听流式响应开始
  const onResponseStart = (callback: () => void) => {
    if (!socket.value) return
    
    socket.value.on('response_start', () => {
      currentStreamingMessage.value = {
        id: `streaming_${Date.now()}`,
        content: '',
        isComplete: false
      }
      callback()
    })
  }
  
  // 监听流式响应块
  const onResponseChunk = (callback: (chunk: string) => void) => {
    if (!socket.value) return
    
    socket.value.on('response_chunk', (data: { chunk: string }) => {
      if (currentStreamingMessage.value) {
        currentStreamingMessage.value.content += data.chunk
      }
      callback(data.chunk)
    })
  }
  
  // 监听流式响应结束
  const onResponseEnd = (callback: (fullContent: string) => void) => {
    if (!socket.value) return
    
    socket.value.on('response_end', () => {
      if (currentStreamingMessage.value) {
        currentStreamingMessage.value.isComplete = true
        callback(currentStreamingMessage.value.content)
        currentStreamingMessage.value = null
      }
    })
  }
  
  // 监听错误
  const onError = (callback: (error: { message: string }) => void) => {
    if (!socket.value) return
    
    socket.value.on('error', callback)
  }
  
  // 监听聊天加入成功
  const onChatJoined = (callback: (data: any) => void) => {
    if (!socket.value) return
    
    socket.value.on('chat_joined', callback)
  }
  
  // 移除所有监听器
  const removeAllListeners = () => {
    if (!socket.value) return
    
    socket.value.removeAllListeners('message_received')
    socket.value.removeAllListeners('response_start')
    socket.value.removeAllListeners('response_chunk')
    socket.value.removeAllListeners('response_end')
    socket.value.removeAllListeners('error')
    socket.value.removeAllListeners('chat_joined')
  }
  
  // 设置自动加入回调
  const setAutoJoinCallback = (callback: () => void) => {
    autoJoinCallback.value = callback
  }
  
  return {
    // 状态
    isConnected: computed(() => isConnected.value),
    isConnecting: computed(() => isConnecting.value),
    currentStreamingMessage: computed(() => currentStreamingMessage.value),
    
    // 方法
    connect,
    disconnect,
    joinChat,
    sendMessage,
    setAutoJoinCallback,
    
    // 事件监听
    onMessageReceived,
    onResponseStart,
    onResponseChunk,
    onResponseEnd,
    onError,
    onChatJoined,
    removeAllListeners
  }
}
