<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo and Title -->
      <div class="text-center">
        <div class="mx-auto h-12 w-12 bg-gray-600 rounded-lg flex items-center justify-center">
          <svg class="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h2 class="mt-6 text-3xl font-bold text-gray-900">Reset Password</h2>
        <p class="mt-2 text-sm text-gray-600">
          Enter your email address and we'll send you a link to reset your password
        </p>
      </div>

      <!-- Success State -->
      <Transition
        enter-active-class="transition ease-out duration-300"
        enter-from-class="transform opacity-0 scale-95"
        enter-to-class="transform opacity-100 scale-100"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="transform opacity-100 scale-100"
        leave-to-class="transform opacity-0 scale-95"
      >
        <div v-if="emailSent" class="text-center space-y-6">
          <!-- Success Icon -->
          <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
            <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>

          <!-- Success Message -->
          <div class="space-y-2">
            <h3 class="text-lg font-medium text-gray-900">Check your email</h3>
            <p class="text-sm text-gray-600">
              We've sent a password reset link to <span class="font-medium">{{ form.email }}</span>
            </p>
            <p class="text-xs text-gray-500">
              Didn't receive the email? Check your spam folder or try again in a few minutes.
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="space-y-3">
            <button
              type="button"
              @click="resetForm"
              class="w-full btn-secondary py-3 text-base font-medium"
            >
              Try different email
            </button>
            <RouterLink 
              to="/login" 
              class="block w-full text-center btn-primary py-3 text-base font-medium rounded-md"
            >
              Back to login
            </RouterLink>
          </div>

          <!-- Resend Timer -->
          <div v-if="resendTimer > 0" class="text-xs text-gray-500">
            You can request another email in {{ resendTimer }} seconds
          </div>
          <button
            v-else-if="emailSent"
            type="button"
            @click="handleResend"
            :disabled="loading"
            class="text-sm text-primary-600 hover:text-primary-500 disabled:opacity-50"
          >
            Resend email
          </button>
        </div>
      </Transition>

      <!-- Form State -->
      <Transition
        enter-active-class="transition ease-out duration-300"
        enter-from-class="transform opacity-0 scale-95"
        enter-to-class="transform opacity-100 scale-100"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="transform opacity-100 scale-100"
        leave-to-class="transform opacity-0 scale-95"
      >
        <form v-if="!emailSent" class="mt-8 space-y-6" @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <!-- Email Field -->
            <div>
              <label for="email" class="form-label">Email address</label>
              <div class="mt-1 relative">
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  autocomplete="email"
                  required
                  class="form-input"
                  :class="{ 'border-red-500': errors.email }"
                  placeholder="Enter your email address"
                  @blur="validateEmail"
                  :disabled="loading"
                />
                <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              <p v-if="errors.email" class="form-error">{{ errors.email }}</p>
              <p v-else class="mt-1 text-xs text-gray-500">
                We'll send you a secure link to reset your password
              </p>
            </div>
          </div>

          <!-- Submit Button -->
          <div>
            <button
              type="submit"
              :disabled="loading || !!errors.email"
              class="w-full btn-primary py-3 text-base font-medium"
            >
              <span v-if="!loading">Send reset link</span>
              <span v-else class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending...
              </span>
            </button>
          </div>

          <!-- Error Alert -->
          <Transition
            enter-active-class="transition ease-out duration-300"
            enter-from-class="transform opacity-0 scale-95"
            enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition ease-in duration-200"
            leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95"
          >
            <div v-if="errorMessage" class="rounded-md bg-red-50 p-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm text-red-800">{{ errorMessage }}</p>
                </div>
              </div>
            </div>
          </Transition>

          <!-- Back to Login Link -->
          <div class="text-center">
            <RouterLink to="/login" class="text-sm font-medium text-primary-600 hover:text-primary-500">
              ← Back to login
            </RouterLink>
          </div>
        </form>
      </Transition>

      <!-- Security Notice -->
      <div class="flex items-center justify-center text-xs text-gray-500">
        <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <span>Secure Connection</span>
        <span class="mx-1">·</span>
        <span>Your data is protected with TLS encryption</span>
      </div>

      <!-- Additional Information -->
      <div v-if="!emailSent" class="mt-6 p-4 bg-blue-50 rounded-lg">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-blue-800">Password Reset Information</h3>
            <div class="mt-2 text-sm text-blue-700">
              <ul class="list-disc pl-5 space-y-1">
                <li>Reset links expire after 24 hours for security</li>
                <li>You can only request a new reset every 5 minutes</li>
                <li>Check your spam folder if you don't receive the email</li>
                <li>Contact support if you continue to have issues</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { validateEmail as validateEmailUtil } from '@/utils/validation'

// Form state
const form = reactive({
  email: ''
})

// UI state
const loading = ref(false)
const emailSent = ref(false)
const errorMessage = ref('')
const resendTimer = ref(0)

// Form validation
const errors = reactive({
  email: ''
})

// Timer reference for cleanup
let timerInterval: number | null = null

// Validation methods
const validateEmail = () => {
  if (!form.email) {
    errors.email = 'Email address is required'
  } else if (!validateEmailUtil(form.email)) {
    errors.email = 'Please enter a valid email address'
  } else {
    errors.email = ''
  }
}

const validateForm = () => {
  validateEmail()
  return !errors.email
}

// Timer management
const startResendTimer = () => {
  resendTimer.value = 300 // 5 minutes
  timerInterval = setInterval(() => {
    resendTimer.value--
    if (resendTimer.value <= 0) {
      if (timerInterval !== null) {
        clearInterval(timerInterval)
      }
      timerInterval = null
    }
  }, 1000)
}

// Submit handler
const handleSubmit = async () => {
  errorMessage.value = ''
  
  if (!validateForm()) {
    return
  }
  
  loading.value = true
  
  try {
    // TODO: Replace with actual API call
    // await authStore.requestPasswordReset(form.email)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Success
    emailSent.value = true
    startResendTimer()
    
  } catch (error: any) {
    console.error('Password reset request failed:', error)
    
    if (error.response?.status === 404) {
      errorMessage.value = 'No account found with this email address'
    } else if (error.response?.status === 429) {
      errorMessage.value = 'Too many requests. Please try again later'
    } else {
      errorMessage.value = error.response?.data?.error_description || 'An error occurred. Please try again'
    }
  } finally {
    loading.value = false
  }
}

// Resend handler
const handleResend = async () => {
  if (resendTimer.value > 0) return
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    // TODO: Replace with actual API call
    // await authStore.requestPasswordReset(form.email)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    startResendTimer()
    
  } catch (error: any) {
    console.error('Resend failed:', error)
    errorMessage.value = 'Failed to resend email. Please try again'
  } finally {
    loading.value = false
  }
}

// Reset form to initial state
const resetForm = () => {
  emailSent.value = false
  form.email = ''
  errors.email = ''
  errorMessage.value = ''
  resendTimer.value = 0
  
  if (timerInterval !== null) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

// Cleanup on unmount
onUnmounted(() => {
  if (timerInterval !== null) {
    clearInterval(timerInterval)
  }
})
</script>

<style scoped>
/* Component-specific styles if needed */
</style>

 
