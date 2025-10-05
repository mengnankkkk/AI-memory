export interface Companion {
  id: number
  user_id: string
  name: string
  avatar_id: string
  personality_archetype: string
  custom_greeting?: string
  greeting: string
}

export interface CompanionCreate {
  user_id: string
  name: string
  avatar_id: string
  personality_archetype: string
  custom_greeting?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
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
