<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo and Title -->
      <div class="text-center">
        <div class="mx-auto h-12 w-12 bg-gray-900 rounded-lg flex items-center justify-center">
          <CalendarIcon class="h-8 w-8 text-white" />
        </div>
        <h2 class="mt-6 text-3xl font-bold text-gray-900">EventManager</h2>
        <p class="mt-2 text-sm text-gray-600">Sign in to your account</p>
      </div>

      <!-- Login Form -->
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div v-if="!mfaRequired" class="space-y-4">
          <BaseInput
            id="email"
            v-model="credentials.email"
            type="email"
            label="Email address"
            required
            autocomplete="email"
            placeholder="you@example.com"
          />
          <BaseInput
            id="password"
            v-model="credentials.password"
            type="password"
            label="Password"
            required
            autocomplete="current-password"
            placeholder="••••••••"
          />
        </div>
        
        <div v-if="mfaRequired" class="space-y-4">
            <p class="text-center text-sm text-gray-600">Enter the code from your authenticator app.</p>
            <BaseInput
              id="mfa_code"
              v-model="credentials.mfa_code"
              type="text"
              label="Two-Factor Code"
              required
              autocomplete="one-time-code"
              placeholder="123456"
            />
        </div>

        <div v-if="!mfaRequired" class="flex items-center justify-between">
          <div class="text-sm">
            <RouterLink to="/forgot-password" class="font-medium text-blue-600 hover:text-blue-500">
              Forgot your password?
            </RouterLink>
          </div>
        </div>

        <div>
          <BaseButton type="submit" :disabled="loading" full-width>
            <span v-if="!loading">{{ mfaRequired ? 'Verify' : 'Sign in' }}</span>
            <span v-else>Loading...</span>
          </BaseButton>
        </div>
        
        <div v-if="errorMessage" class="text-red-500 text-sm text-center">
          {{ errorMessage }}
        </div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { CalendarIcon } from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

const credentials = reactive({
  email: '',
  password: '',
  mfa_code: ''
})

const loading = ref(false)
const errorMessage = ref('')
const mfaRequired = ref(false)

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await authStore.login(credentials)
  } catch (error: unknown) {
    if (error instanceof Error && 'response' in error) {
      const err = error as { response?: { status: number, data?: { detail?: string } } }
      const status = err.response?.status
      const detail = err.response?.data?.detail

      if (status === 423) {
        mfaRequired.value = true
        // Don't set an error message here, just show the MFA field
      } else if (status === 401) {
        errorMessage.value = detail || 'Invalid email or password.'
      } else {
        errorMessage.value = detail || 'An unexpected error occurred. Please try again.'
      }
    } else {
      errorMessage.value = 'An unexpected error occurred. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

 
