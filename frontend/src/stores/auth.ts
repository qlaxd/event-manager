import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'
import type { User, LoginRequest } from '@/types'
import authService from '@/services/auth'
import apiClient from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const returnUrl = ref<string | null>(null)

  // On store init, set Authorization header if token exists
  if (accessToken.value) {
    apiClient.defaults.headers.common.Authorization = `Bearer ${accessToken.value}`
  }

  // Actions
  async function login(credentials: LoginRequest) {
    try {
      const response = await authService.login(credentials)
      accessToken.value = response.access_token
      localStorage.setItem('access_token', response.access_token)
      apiClient.defaults.headers.common.Authorization = `Bearer ${response.access_token}`

      await fetchUser()

      router.push(returnUrl.value || '/dashboard')
      returnUrl.value = null
    } catch (error: unknown) {
      // If MFA is required, the component will handle it, so we don't need to log here.
      if (error instanceof Error && 'response' in error && (error.response as any)?.status === 423) {
        throw error;
      }
      console.error('Login failed:', error)
      // Re-throw the error to be handled by the component
      throw error
    }
  }

  async function fetchUser() {
    if (!accessToken.value) return

    try {
      const userData = await authService.getProfile()
      user.value = userData
    } catch (error) {
      console.error('Failed to fetch user:', error)
      await logout() // If we can't get user, the token is likely invalid
      throw error
    }
  }

  async function logout() {
    try {
      // Ask the backend to revoke the refresh token (if it exists)
      await authService.logout()
    } catch (error) {
      console.error('Backend logout failed, proceeding with client-side cleanup.', error)
    } finally {
      // Always clear client-side session data
      user.value = null
      accessToken.value = null
      localStorage.removeItem('access_token')
      delete apiClient.defaults.headers.common.Authorization

      // Redirect to login page
      if (router.currentRoute.value.name !== 'login') {
        router.push('/login')
      }
    }
  }

  async function trySilentRefresh() {
    if (accessToken.value) return
    try {
      // Send empty body; backend will read refresh token from HttpOnly cookie
      const response = await apiClient.post('/auth/refresh', {})
      const { access_token } = response.data
      setAccessToken(access_token)
      await fetchUser()
    } catch (error: any) {
      // Only logout if error is 401/403 (real auth error), not just validation error
      const status = error?.response?.status
      if (status === 401 || status === 403) {
        await logout()
      }
      // Otherwise, do not force logout (e.g. validation error)
    }
  }

  function setReturnUrl(url: string) {
    returnUrl.value = url
  }

  function setAccessToken(token: string) {
    accessToken.value = token
    if (token) {
      localStorage.setItem('access_token', token)
      apiClient.defaults.headers.common.Authorization = `Bearer ${token}`
    } else {
      localStorage.removeItem('access_token')
      delete apiClient.defaults.headers.common.Authorization
    }
  }

  return {
    user,
    accessToken,
    isAuthenticated,
    returnUrl,
    login,
    fetchUser,
    logout,
    setReturnUrl,
    setAccessToken,
    trySilentRefresh, // export the new method
  }
})
