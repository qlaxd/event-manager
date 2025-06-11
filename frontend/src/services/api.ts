import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { getToken, setToken, removeToken, isTokenExpired } from '@/utils/auth'
import router from '@/router'

// Create axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000, // 10 seconds
  withCredentials: true // Important: Send cookies with requests (for refresh token)
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
      // Add the token to the Authorization header
      config.headers.Authorization = `Bearer ${token}`
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
      
      // Only attempt to refresh the token if we're not already doing so
      if (!isRefreshing) {
        isRefreshing = true
        
        try {
          // The refresh token is sent automatically as an HttpOnly cookie
          const response = await axios.post(`${originalRequest.baseURL}/auth/refresh`, {
            grant_type: 'refresh_token'
          }, {
            withCredentials: true // Important: Send cookies with the request
          })
          
          const { access_token } = response.data
          
          // Store new access token in memory
          setToken('access', access_token)
          
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
          router.push('/login')
          return Promise.reject(refreshError)
        }
      } else {
        // Wait for the token to be refreshed
        return new Promise(resolve => {
          subscribeTokenRefresh((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(apiClient(originalRequest))
          })
        })
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