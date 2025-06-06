import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest } from '@/types'
import authService from '@/services/auth'
import { setToken, removeToken, getToken } from '@/utils/auth'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  rememberMe: boolean
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(getToken('access'))
  const refreshToken = ref<string | null>(getToken('refresh'))
  const rememberMe = ref(false)

  // Computed
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const hasMFA = computed(() => user.value?.mfa_enabled || false)

  // Actions
  const login = async (credentials: LoginRequest & { rememberMe?: boolean }) => {
    try {
      rememberMe.value = credentials.rememberMe || false
      
      const response = await authService.login({
        email: credentials.email,
        password: credentials.password,
        mfa_code: credentials.mfa_code
      })

      if (response.mfa_required) {
        return { mfa_required: true }
      }

      // Store tokens
      setToken('access', response.access_token, rememberMe.value)
      setToken('refresh', response.refresh_token, rememberMe.value)
      
      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token

      // Fetch user profile
      await fetchUser()

      return response
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  const verifyMFA = async (credentials: LoginRequest) => {
    try {
      const response = await authService.login({
        email: credentials.email,
        password: credentials.password,
        mfa_code: credentials.mfa_code
      })

      // Store tokens
      setToken('access', response.access_token, rememberMe.value)
      setToken('refresh', response.refresh_token, rememberMe.value)
      
      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token

      // Fetch user profile
      await fetchUser()

      return response
    } catch (error) {
      console.error('MFA verification error:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      // Optional: Call logout endpoint
      // await authService.logout()
      
      // Clear tokens
      removeToken('access')
      removeToken('refresh')
      
      // Clear state
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      rememberMe.value = false
    } catch (error) {
      console.error('Logout error:', error)
      // Even if logout fails, clear local state
      removeToken('access')
      removeToken('refresh')
      user.value = null
      accessToken.value = null
      refreshToken.value = null
    }
  }

  const fetchUser = async () => {
    try {
      const userData = await authService.getProfile()
      user.value = userData
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      throw error
    }
  }

  const refreshAccessToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }

      const response = await authService.refreshToken({
        grant_type: 'refresh_token',
        refresh_token: refreshToken.value
      })

      // Update tokens
      setToken('access', response.access_token, rememberMe.value)
      setToken('refresh', response.refresh_token, rememberMe.value)
      
      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token

      return response
    } catch (error) {
      console.error('Token refresh error:', error)
      // If refresh fails, logout user
      await logout()
      throw error
    }
  }

  const initializeAuth = async () => {
    // Check if we have tokens on app start
    if (accessToken.value && refreshToken.value) {
      try {
        await fetchUser()
      } catch (error) {
        // If fetching user fails, try refreshing token
        try {
          await refreshAccessToken()
          await fetchUser()
        } catch (refreshError) {
          // If refresh also fails, logout
          await logout()
        }
      }
    }
  }

  const updateUser = (updatedUser: User) => {
    user.value = updatedUser
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    rememberMe,
    
    // Computed
    isAuthenticated,
    hasMFA,
    
    // Actions
    login,
    verifyMFA,
    logout,
    fetchUser,
    refreshAccessToken,
    initializeAuth,
    updateUser
  }
}) 