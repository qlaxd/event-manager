import apiClient from './api'
import type { LoginRequest, User } from '@/types'

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  scope?: string
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

  async getProfile(): Promise<User> {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  }

  async logout(): Promise<void> {
    // The backend will read the HttpOnly refresh token cookie
    await apiClient.post('/auth/revoke');
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
  }> {
    const response = await apiClient.post<{
      secret: string
      qr_code: string
    }>('/auth/mfa/enable', {
      password
    });
    return response.data;
  }

  async verifyMFASetup(mfaCode: string): Promise<{ backup_codes: string[] }> {
    const response = await apiClient.post<{ backup_codes: string[] }>('/auth/mfa/verify', {
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

  async refresh(): Promise<TokenResponse> {
    // Send empty body; backend will read refresh token from HttpOnly cookie
    const response = await apiClient.post<TokenResponse>('/auth/refresh', {});
    return response.data;
  }
}

export default new AuthService();
