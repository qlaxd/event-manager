// Token storage keys
const ACCESS_TOKEN_KEY = 'ucc_access_token'
const REFRESH_TOKEN_KEY = 'ucc_refresh_token'
const USER_KEY = 'ucc_user'

// Token storage helpers
export const setToken = (type: 'access' | 'refresh', token: string, rememberMe: boolean = false): void => {
  const key = type === 'access' ? ACCESS_TOKEN_KEY : REFRESH_TOKEN_KEY
  
  if (rememberMe) {
    // Store in localStorage for persistent storage
    localStorage.setItem(key, token)
    // Also store in sessionStorage for current session
    sessionStorage.setItem(key, token)
  } else {
    // Store only in sessionStorage
    sessionStorage.setItem(key, token)
  }
}

export const getToken = (type: 'access' | 'refresh'): string | null => {
  const key = type === 'access' ? ACCESS_TOKEN_KEY : REFRESH_TOKEN_KEY
  
  // Check sessionStorage first
  const sessionToken = sessionStorage.getItem(key)
  if (sessionToken) return sessionToken
  
  // Fall back to localStorage
  const localToken = localStorage.getItem(key)
  if (localToken) {
    // Copy to sessionStorage for faster access
    sessionStorage.setItem(key, localToken)
  }
  
  return localToken
}

export const removeToken = (type: 'access' | 'refresh'): void => {
  const key = type === 'access' ? ACCESS_TOKEN_KEY : REFRESH_TOKEN_KEY
  sessionStorage.removeItem(key)
  localStorage.removeItem(key)
}

export const clearAllTokens = (): void => {
  removeToken('access')
  removeToken('refresh')
  sessionStorage.removeItem(USER_KEY)
  localStorage.removeItem(USER_KEY)
}

// JWT token helpers
export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = parseJWT(token)
    if (!payload.exp) return false
    
    const currentTime = Date.now() / 1000
    return payload.exp < currentTime
  } catch {
    return true
  }
}

export const getTokenExpiration = (token: string): Date | null => {
  try {
    const payload = parseJWT(token)
    if (!payload.exp) return null
    
    return new Date(payload.exp * 1000)
  } catch {
    return null
  }
}

export const parseJWT = (token: string): any => {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    
    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Failed to parse JWT:', error)
    throw error
  }
}

// Session management
export const isAuthenticated = (): boolean => {
  const accessToken = getToken('access')
  if (!accessToken) return false
  
  return !isTokenExpired(accessToken)
}

// Cross-tab synchronization
export const setupAuthSync = (callback: () => void): void => {
  window.addEventListener('storage', (event) => {
    if (event.key === ACCESS_TOKEN_KEY || event.key === REFRESH_TOKEN_KEY) {
      // Token changed in another tab
      callback()
    }
  })
}

// Security headers
export const getAuthHeaders = (): Record<string, string> => {
  const token = getToken('access')
  if (!token) return {}
  
  return {
    'Authorization': `Bearer ${token}`
  }
} 