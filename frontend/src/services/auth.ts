import apiClient from './api'
import type { LoginRequest, User } from '@/types'

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  scope?: string
  mfa_required?: boolean
}

interface RefreshTokenRequest {
  grant_type: 'refresh_token'
  refresh_token: string
}

class AuthService {
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/token', credentials)
    return response.data
  }

  async refreshToken(data: RefreshTokenRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/refresh', data)
    return response.data
  }

  async getProfile(): Promise<User> {
    const response = await apiClient.get<User>('/users/me')
    return response.data
  }

  async logout(): Promise<void> {
    // Optional: Call backend logout endpoint
    // await apiClient.post('/auth/logout')
  }

  async requestPasswordReset(email: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/auth/request-password-reset', {
      email
    })
    return response.data
  }

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/auth/reset-password', {
      token,
      new_password: newPassword
    })
    return response.data
  }

  async setupMFA(): Promise<{
    secret: string
    qr_code: string
    backup_codes: string[]
  }> {
    const response = await apiClient.post<{
      secret: string
      qr_code: string
      backup_codes: string[]
    }>('/auth/mfa/setup')
    return response.data
  }

  async verifyMFA(code: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/auth/mfa/verify', {
      code
    })
    return response.data
  }

  async disableMFA(password: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/auth/mfa/disable', {
      password
    })
    return response.data
  }
}

export default new AuthService() 