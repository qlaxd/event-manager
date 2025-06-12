import apiClient from './api'
import type { User } from '@/types'

interface UpdateProfileRequest {
  full_name: string
  email: string
}

interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

interface ProfileUpdateResponse {
  message: string
  user: User
}

class UserService {
  async updateProfile(data: UpdateProfileRequest): Promise<ProfileUpdateResponse> {
    const response = await apiClient.patch<ProfileUpdateResponse>('/users/me', data)
    return response.data
  }

  async changePassword(data: ChangePasswordRequest): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/users/me/change-password', data)
    return response.data
  }
}

export default new UserService()
