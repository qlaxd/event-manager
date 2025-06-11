import apiClient from './api'
import type { LoginRequest, User } from '@/types'

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  scope?: string
}

interface RefreshTokenRequest {
  grant_type: 'refresh_token'
  refresh_token: string
}

class AuthService {
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    // Transform to OAuth2 password flow format
    const params = new URLSearchParams();
    params.append('grant_type', 'password');
    params.append('username', credentials.email);
    params.append('password', credentials.password);
    
    if (credentials.mfa_code) {
      params.append('mfa_code', credentials.mfa_code);
    }
    
    const response = await apiClient.post<TokenResponse>('/auth/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const params = new URLSearchParams();
    params.append('grant_type', 'refresh_token');
    params.append('refresh_token', refreshToken);
    
    const response = await apiClient.post<TokenResponse>('/auth/refresh', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    return response.data;
  }

  async getProfile(): Promise<User> {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  }

  async logout(token: string): Promise<void> {
    await apiClient.post('/auth/revoke', {
      token,
      token_type_hint: 'refresh_token'
    });
  }

  async requestPasswordReset(email: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/auth/password-reset/request', {
      email
    });
    return response.data;
  }

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/auth/password-reset/confirm', {
      token,
      new_password: newPassword
    });
    return response.data;
  }

  async enableMFA(password: string): Promise<{
    secret: string
    qr_code: string
    backup_codes: string[]
  }> {
    const response = await apiClient.post<{
      secret: string
      qr_code: string
      backup_codes: string[]
    }>('/auth/mfa/enable', {
      password
    });
    return response.data;
  }

  async verifyMFASetup(mfaCode: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/auth/mfa/verify', {
      mfa_code: mfaCode
    });
    return response.data;
  }

  async disableMFA(password: string, mfaCode: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/auth/mfa/disable', {
      password,
      mfa_code: mfaCode
    });
    return response.data;
  }
}

export default new AuthService(); 