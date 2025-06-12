export interface User {
    id: string
    email: string
    full_name: string
    mfa_enabled: boolean
  }
  
  export interface Event {
    id: string
    title: string
    occurrence: string
    description?: string
    created_at: string
    updated_at: string
  }
  
  export interface EventCreate {
    title: string
    occurrence: string
    description?: string
  }
  
  export interface EventUpdate {
    title?: string
    occurrence?: string
    description?: string
  }
  
  export interface LoginRequest {
    email: string
    password: string
    mfa_code?: string
  }
  
  export interface ChatMessage {
    id: string
    sender: 'user' | 'bot'
    message: string
    timestamp: string
    quick_replies?: string[]
  }

  export interface ChatMessageRequest {
    message: string
    session_id: string
  }

  export interface ChatMessageResponse {
    response: string
    session_id: string
    quick_replies?: string[]
  }

  export interface EscalateRequest {
    session_id: string
    reason: string
    message: string
  }

  export interface EscalateResponse {
    message: string
  }