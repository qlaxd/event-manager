// Token storage keys
const ACCESS_TOKEN_KEY = 'ucc_access_token'
const USER_KEY = 'ucc_user'

// In-memory token storage for access token (more secure than localStorage or sessionStorage)
let inMemoryToken: string | null = null;

// Token storage helpers
export const setToken = (type: 'access', token: string): void => {
  if (type === 'access') {
    // Store access token in memory only, not in localStorage or sessionStorage
    inMemoryToken = token;
  }
}

export const getToken = (type: 'access' | 'refresh'): string | null => {
  if (type === 'access') {
    // Return the in-memory token
    return inMemoryToken;
  } else if (type === 'refresh') {
    // The refresh token is managed by the browser as an HttpOnly cookie
    // We don't have direct access to it from JavaScript
    return null;
  }
  return null;
}

export const removeToken = (type: 'access'): void => {
  if (type === 'access') {
    inMemoryToken = null;
  }
}

export const clearAllTokens = (): void => {
  removeToken('access');
  sessionStorage.removeItem(USER_KEY);
  localStorage.removeItem(USER_KEY);
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

// Security headers
export const getAuthHeaders = (): Record<string, string> => {
  const token = getToken('access')
  if (!token) return {}
  
  return {
    'Authorization': `Bearer ${token}`
  }
} 