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
  
  export interface LoginRequest {
    email: string
    password: string
    mfa_code?: string
  }