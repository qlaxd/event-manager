<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div class="text-center">
        <div class="mx-auto h-12 w-12 bg-gray-600 rounded-lg flex items-center justify-center">
          <svg class="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h2 class="mt-6 text-3xl font-bold text-gray-900">Set a New Password</h2>
        <p class="mt-2 text-sm text-gray-600">
          Please enter your new password below.
        </p>
      </div>

      <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded p-4 text-center">
        <div class="text-green-700 font-semibold mb-2">{{ successMessage }}</div>
        <RouterLink to="/login" class="text-blue-600 hover:underline">Go to Login</RouterLink>
      </div>

      <form v-else @submit.prevent="handleSubmit" class="space-y-6">
        <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded p-2 text-red-700 text-sm text-center">{{ errorMessage }}</div>
        <div>
          <label for="new-password" class="block text-sm font-medium text-gray-700">New Password</label>
          <input
            id="new-password"
            type="password"
            v-model="newPassword"
            autocomplete="new-password"
            class="mt-1 block w-full rounded border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
            :disabled="loading"
            required
          />
        </div>
        <div>
          <label for="confirm-password" class="block text-sm font-medium text-gray-700">Confirm New Password</label>
          <input
            id="confirm-password"
            type="password"
            v-model="confirmPassword"
            autocomplete="new-password"
            class="mt-1 block w-full rounded border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
            :disabled="loading"
            required
          />
        </div>
        <div>
          <PasswordStrengthIndicator :password="newPassword" />
        </div>
        <button
          type="submit"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          :disabled="loading"
        >
          <span v-if="loading">Setting Password...</span>
          <span v-else>Set New Password</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import AuthService from '@/services/auth'
import { validatePassword, calculatePasswordStrength } from '@/utils/validation'
import { defineComponent, computed } from 'vue'

const route = useRoute()
const router = useRouter()

const token = ref<string | null>(null)
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

onMounted(() => {
  token.value = (route.query.token as string) || (route.params.token as string) || null
  if (!token.value) {
    errorMessage.value = 'Invalid or missing password reset link.'
  }
})

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''

  if (!token.value) {
    errorMessage.value = 'Invalid or missing password reset link.'
    return
  }

  if (!newPassword.value || !confirmPassword.value) {
    errorMessage.value = 'Please fill in all fields.'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
    return
  }
  const { isValid, errors } = validatePassword(newPassword.value)
  if (!isValid) {
    errorMessage.value = errors.join(' ')
    return
  }

  loading.value = true
  try {
    await AuthService.resetPassword(token.value, newPassword.value)
    loading.value = false
    newPassword.value = ''
    confirmPassword.value = ''
    successMessage.value = 'Your password has been reset successfully. You can now log in.'
  } catch (error: any) {
    loading.value = false
    const status = error?.response?.status
    if ([400, 404, 422].includes(status)) {
      errorMessage.value = 'This password reset link is invalid or has expired. Please try again.'
    } else if (status === 429) {
      errorMessage.value = 'You have made too many attempts. Please try again later.'
    } else {
      errorMessage.value = 'An unexpected error occurred. Please try again.'
    }
  }
}

const PasswordStrengthIndicator = defineComponent({
  name: 'PasswordStrengthIndicator',
  props: {
    password: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const strength = computed(() => calculatePasswordStrength(props.password))
    return { strength, props }
  },
  template: `
    <div v-if="props.password" class="mt-2">
      <div class="flex items-center space-x-2">
        <div class="w-full h-2 rounded bg-gray-200">
          <div :class="{
            'bg-red-500': strength.strength === 'weak',
            'bg-yellow-400': strength.strength === 'fair',
            'bg-blue-400': strength.strength === 'good',
            'bg-green-500': strength.strength === 'strong'
          }" :style="{ width: (strength.score * 12.5) + '%' }" class="h-2 rounded transition-all"></div>
        </div>
        <span class="text-xs font-medium" :class="{
          'text-red-500': strength.strength === 'weak',
          'text-yellow-600': strength.strength === 'fair',
          'text-blue-600': strength.strength === 'good',
          'text-green-600': strength.strength === 'strong'
        }">{{ strength.strength.charAt(0).toUpperCase() + strength.strength.slice(1) }}</span>
      </div>
      <ul class="text-xs text-gray-500 mt-1 list-disc pl-5">
        <li>Password must be at least 8 characters</li>
        <li>At least one uppercase and one lowercase letter</li>
        <li>At least one number</li>
      </ul>
    </div>
  `
})
</script>

<style scoped>
/* Add any additional styling if needed */
</style>
