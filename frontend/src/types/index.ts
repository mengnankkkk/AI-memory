export interface Companion {
  id: number
  user_id: string
  name: string
  avatar_id: string | number
  personality_archetype: string
  custom_greeting?: string
  greeting?: string
  created_at?: string
  session_count?: number
}

export interface CompanionCreate {
  name: string
  avatar_id: string
  personality_archetype: string
  custom_greeting?: string
}

export interface ChatMessage {
  id?: number
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface ChatRequest {
  companion_id: number
  message: string
  session_id: string
}

export interface ChatResponse {
  message: string
  companion_name: string
}
