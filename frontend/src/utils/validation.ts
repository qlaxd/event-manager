// Email validation
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Password validation
export const validatePassword = (password: string): {
  isValid: boolean
  errors: string[]
} => {
  const errors: string[] = []

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long')
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter')
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter')
  }

  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

// Password strength calculator
export const calculatePasswordStrength = (password: string): {
  score: number
  strength: 'weak' | 'fair' | 'good' | 'strong'
} => {
  let score = 0

  // Length
  if (password.length >= 8) score++
  if (password.length >= 12) score++
  if (password.length >= 16) score++

  // Character variety
  if (/[a-z]/.test(password)) score++
  if (/[A-Z]/.test(password)) score++
  if (/[0-9]/.test(password)) score++
  if (/[^a-zA-Z0-9]/.test(password)) score++

  // Pattern complexity
  if (!/(.)\1{2,}/.test(password)) score++ // No repeated characters
  if (!/^[0-9]+$/.test(password) && !/^[a-zA-Z]+$/.test(password)) score++ // Not all letters or numbers

  // Determine strength
  let strength: 'weak' | 'fair' | 'good' | 'strong'
  if (score <= 3) strength = 'weak'
  else if (score <= 5) strength = 'fair'
  else if (score <= 7) strength = 'good'
  else strength = 'strong'

  return { score, strength }
}

// TOTP code validation (6 digits)
export const validateTOTPCode = (code: string): boolean => {
  return /^\d{6}$/.test(code)
}

// Required field validation
export const required = (value: string | number | null | undefined, fieldName: string = 'Field'): string | null => {
  if (!value || (typeof value === 'string' && !value.trim())) {
    return `${fieldName} is required`
  }
  return null
}

// Min length validation
export const minLength = (value: string, min: number, fieldName: string = 'Field'): string | null => {
  if (!value || value.length < min) {
    return `${fieldName} must be at least ${min} characters`
  }
  return null
}

// Max length validation
export const maxLength = (value: string, max: number, fieldName: string = 'Field'): string | null => {
  if (value && value.length > max) {
    return `${fieldName} must be no more than ${max} characters`
  }
  return null
}

// Date validation
export const isValidDate = (date: string | Date): boolean => {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj instanceof Date && !isNaN(dateObj.getTime())
}

// Future date validation
export const isFutureDate = (date: string | Date): boolean => {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return isValidDate(dateObj) && dateObj > new Date()
}

// Compose validators
export const composeValidators = (...validators: Array<(value: string | number | null | undefined) => string | null>) => {
  return (value: string | number | null | undefined): string | null => {
    for (const validator of validators) {
      const error = validator(value)
      if (error) return error
    }
    return null
  }
} 