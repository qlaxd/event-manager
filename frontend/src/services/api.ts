import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { getToken, setToken, removeToken, isTokenExpired } from '@/utils/auth'
import router from '@/router'

// Create axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000 // 30 seconds
})

// Track if we're currently refreshing the token
let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

// Subscribe to token refresh
const subscribeTokenRefresh = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback)
}

// Notify all subscribers when token is refreshed
const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

// Request interceptor
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const token = getToken('access')
    
    if (token && config.headers) {
      // Check if token is expired
      if (isTokenExpired(token)) {
        // Wait for token refresh if already in progress
        if (isRefreshing) {
          return new Promise(resolve => {
            subscribeTokenRefresh((newToken: string) => {
              config.headers!.Authorization = `Bearer ${newToken}`
              resolve(config)
            })
          })
        }
        
        // Otherwise, trigger token refresh
        isRefreshing = true
        
        try {
          const refreshToken = getToken('refresh')
          if (!refreshToken) throw new Error('No refresh token')
          
          const response = await axios.post(`${config.baseURL}/auth/refresh`, {
            grant_type: 'refresh_token',
            refresh_token: refreshToken
          })
          
          const { access_token, refresh_token } = response.data
          
          // Store new tokens
          setToken('access', access_token)
          setToken('refresh', refresh_token)
          
          // Update current request
          config.headers.Authorization = `Bearer ${access_token}`
          
          // Notify subscribers
          onTokenRefreshed(access_token)
          
          isRefreshing = false
        } catch (error) {
          isRefreshing = false
          removeToken('access')
          removeToken('refresh')
          router.push('/login')
          return Promise.reject(error)
        }
      } else {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  response => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // Try to refresh token
      const refreshToken = getToken('refresh')
      if (refreshToken && !isRefreshing) {
        isRefreshing = true
        
        try {
          const response = await axios.post(`${originalRequest.baseURL}/auth/refresh`, {
            grant_type: 'refresh_token',
            refresh_token: refreshToken
          })
          
          const { access_token, refresh_token } = response.data
          
          // Store new tokens
          setToken('access', access_token)
          setToken('refresh', refresh_token)
          
          // Update failed request
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          
          // Notify subscribers
          onTokenRefreshed(access_token)
          
          isRefreshing = false
          
          // Retry original request
          return apiClient(originalRequest)
        } catch (refreshError) {
          isRefreshing = false
          removeToken('access')
          removeToken('refresh')
          router.push('/login')
          return Promise.reject(refreshError)
        }
      }
    }
    
    // Handle other errors
    if (error.response?.status === 403) {
      // Forbidden - user doesn't have permission
      console.error('Permission denied')
    } else if (error.response?.status === 500) {
      // Server error
      console.error('Server error')
    }
    
    return Promise.reject(error)
  }
)

export default apiClient