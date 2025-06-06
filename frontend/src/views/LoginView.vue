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
        <h2 class="mt-6 text-3xl font-bold text-gray-900">EventManager</h2>
        <p class="mt-2 text-sm text-gray-600">Sign in to your account</p>
      </div>

      <!-- Login Form -->
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
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
                placeholder="Enter your email"
                @blur="validateEmail"
              />
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <p v-if="errors.email" class="form-error">{{ errors.email }}</p>
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="form-label">Password</label>
            <div class="mt-1 relative">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                required
                class="form-input pr-10"
                :class="{ 'border-red-500': errors.password }"
                placeholder="Enter your password"
              />
              <button
                type="button"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
                @click="showPassword = !showPassword"
              >
                <svg v-if="!showPassword" class="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
            <p v-if="errors.password" class="form-error">{{ errors.password }}</p>
          </div>
        </div>

        <!-- Remember Me & Forgot Password -->
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="form.rememberMe"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-900">
              Remember me
            </label>
          </div>

          <div class="text-sm">
            <RouterLink to="/forgot-password" class="font-medium text-primary-600 hover:text-primary-500">
              Forgot password?
            </RouterLink>
          </div>
        </div>

        <!-- Submit Button -->
        <div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full btn-primary py-3 text-base font-medium"
          >
            <span v-if="!loading">Sign in</span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Signing in...
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
      </form>

      <!-- Security Notice -->
      <div class="flex items-center justify-center text-xs text-gray-500">
        <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <span>Secure Connection</span>
        <span class="mx-1">·</span>
        <span>Your connection is encrypted with TLS</span>
      </div>
    </div>

    <!-- MFA Modal -->
    <MFAModal 
      v-if="showMFAModal"
      @verify="handleMFAVerify"
      @close="showMFAModal = false"
      :loading="loading"
      :error="mfaError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { validateEmail as validateEmailUtil } from '@/utils/validation'
import MFAModal from '@/components/auth/MFAModal.vue'

const router = useRouter()
const authStore = useAuthStore()

// Form state
const form = reactive({
  email: '',
  password: '',
  rememberMe: false
})

// UI state
const loading = ref(false)
const showPassword = ref(false)
const showMFAModal = ref(false)
const errorMessage = ref('')
const mfaError = ref('')

// Form validation
const errors = reactive({
  email: '',
  password: ''
})

// Validation methods
const validateEmail = () => {
  if (!form.email) {
    errors.email = 'Email is required'
  } else if (!validateEmailUtil(form.email)) {
    errors.email = 'Please enter a valid email address'
  } else {
    errors.email = ''
  }
}

const validateForm = () => {
  validateEmail()
  
  if (!form.password) {
    errors.password = 'Password is required'
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
  } else {
    errors.password = ''
  }
  
  return !errors.email && !errors.password
}

// Submit handler
const handleSubmit = async () => {
  errorMessage.value = ''
  
  if (!validateForm()) {
    return
  }
  
  loading.value = true
  
  try {
    const response = await authStore.login({
      email: form.email,
      password: form.password,
      rememberMe: form.rememberMe
    })
    
    if (response.mfa_required) {
      showMFAModal.value = true
    } else {
      // Successful login without MFA
      await router.push('/dashboard')
    }
  } catch (error: any) {
    if (error.response?.status === 401) {
      errorMessage.value = 'Invalid email or password'
    } else if (error.response?.status === 423) {
      showMFAModal.value = true
    } else {
      errorMessage.value = error.response?.data?.error_description || 'An error occurred during login'
    }
  } finally {
    loading.value = false
  }
}

// MFA verification handler
const handleMFAVerify = async (code: string) => {
  mfaError.value = ''
  loading.value = true
  
  try {
    await authStore.verifyMFA({
      email: form.email,
      password: form.password,
      mfa_code: code
    })
    
    showMFAModal.value = false
    await router.push('/dashboard')
  } catch (error: any) {
    mfaError.value = error.response?.data?.error_description || 'Invalid verification code'
  } finally {
    loading.value = false
  }
}
</script>

<!-- bump -->
