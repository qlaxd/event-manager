<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Mobile Header -->
    <header class="lg:hidden bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
      <div class="flex items-center justify-between px-4 py-3">
        <button
          @click="sidebarOpen = true"
          class="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
        >
          <Bars3Icon class="w-6 h-6" />
        </button>
        <div class="flex items-center">
          <div class="flex items-center justify-center w-8 h-8 bg-gray-900 text-white rounded-lg">
            <CalendarIcon class="w-5 h-5" />
          </div>
          <h1 class="ml-3 text-lg font-bold text-gray-900">EventManager</h1>
        </div>
        <div class="w-10"></div> <!-- Spacer for balance -->
      </div>
    </header>

    <!-- Main Layout Container -->
    <div class="flex h-screen lg:h-screen">
      <!-- Left Sidebar -->
      <TheSidebar 
        :user="user" 
        :is-open="sidebarOpen"
        @logout="handleLogout"
        @close="sidebarOpen = false"
      />

      <!-- Main Content -->
      <div class="flex-1 overflow-y-auto w-full">
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <!-- Page Header -->
          <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900">Account Settings</h1>
            <p class="mt-2 text-gray-600">Manage your account security and preferences</p>
          </div>

          <div class="space-y-8">
            <!-- Profile Information Section -->
            <div class="bg-white shadow rounded-lg">
              <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-lg font-semibold text-gray-900">Profile Information</h2>
              </div>
              <div class="px-6 py-6">
                <form @submit.prevent="handleUpdateProfile" class="space-y-6">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <BaseInput
                        v-model="profileForm.full_name"
                        label="Full Name"
                        type="text"
                        required
                        :error="profileErrors.full_name"
                      />
                    </div>
                    <div>
                      <BaseInput
                        v-model="profileForm.email"
                        label="Email Address"
                        type="email"
                        required
                        :error="profileErrors.email"
                      />
                    </div>
                  </div>
                  <div>
                    <BaseButton 
                      type="submit" 
                      variant="primary"
                      :loading="profileLoading"
                      loading-text="Updating..."
                    >
                      Update Profile
                    </BaseButton>
                  </div>
                </form>
              </div>
            </div>

            <!-- Password Section -->
            <div class="bg-white shadow rounded-lg">
              <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-lg font-semibold text-gray-900">Password</h2>
              </div>
              <div class="px-6 py-6">
                <form @submit.prevent="handleChangePassword" class="space-y-6">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <BaseInput
                        v-model="passwordForm.current_password"
                        label="Current Password"
                        type="password"
                        required
                        :error="passwordErrors.current_password"
                      />
                    </div>
                    <div>
                      <BaseInput
                        v-model="passwordForm.new_password"
                        label="New Password"
                        type="password"
                        required
                        :error="passwordErrors.new_password"
                      />
                    </div>
                  </div>
                  <div>
                    <BaseButton 
                      type="submit" 
                      variant="primary"
                      :loading="passwordLoading"
                      loading-text="Changing..."
                    >
                      Change Password
                    </BaseButton>
                  </div>
                </form>
              </div>
            </div>

            <!-- Multi-Factor Authentication Section -->
            <div class="bg-white shadow rounded-lg">
              <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-lg font-semibold text-gray-900">Multi-Factor Authentication</h2>
              </div>
              <div class="px-6 py-6">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-base font-medium text-gray-900">Two-Factor Authentication</h3>
                    <p class="text-sm text-gray-600">Add an extra layer of security to your account</p>
                    <div class="mt-2 flex items-center">
                      <svg 
                        :class="[
                          'h-4 w-4 mr-2',
                          user?.mfa_enabled ? 'text-green-500' : 'text-gray-400'
                        ]" 
                        fill="currentColor" 
                        viewBox="0 0 20 20"
                      >
                        <path 
                          v-if="user?.mfa_enabled"
                          fill-rule="evenodd" 
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" 
                          clip-rule="evenodd" 
                        />
                        <path 
                          v-else
                          fill-rule="evenodd" 
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" 
                          clip-rule="evenodd" 
                        />
                      </svg>
                      <span 
                        :class="[
                          'text-sm font-medium',
                          user?.mfa_enabled ? 'text-green-700' : 'text-gray-500'
                        ]"
                      >
                        {{ user?.mfa_enabled ? 'Enabled' : 'Disabled' }}
                      </span>
                    </div>
                  </div>
                  <div>
                    <BaseButton 
                      v-if="!user?.mfa_enabled"
                      variant="primary"
                      :loading="mfaLoading"
                      @click="showMFASetupModal = true"
                    >
                      Set up MFA
                    </BaseButton>
                    <BaseButton 
                      v-else
                      variant="outline"
                      :loading="mfaLoading"
                      @click="showDisableMFAModal = true"
                    >
                      Disable MFA
                    </BaseButton>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MFA Setup Modal -->
    <BaseModal
      v-model:show="showMFASetupModal"
      title="Set up Two-Factor Authentication"
      size="md"
      :closable="!mfaLoading"
    >
      <div v-if="mfaStep === 'verify_password'" class="space-y-6">
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-4">
            First, please confirm your current password to continue.
          </p>
          <BaseInput
            v-model="mfaPassword"
            label="Current Password"
            type="password"
            required
          />
        </div>
      </div>

      <div v-if="mfaStep === 'scan_qr'" class="space-y-6 text-center">
        <div>
          <p class="text-sm text-gray-600 mb-4">
            Scan the QR code with your authenticator app.
          </p>
          <img :src="mfaQRCode" alt="MFA QR Code" class="mx-auto border p-2 bg-white" />
          <p class="text-sm text-gray-500 mt-1">Or enter this code manually:</p>
          <code class="text-lg bg-gray-100 p-2 rounded">{{ mfaSecret }}</code>
        </div>
        <hr />
        <div>
          <p class="text-sm text-gray-600 mb-4">
            Then, enter the 6-digit code from your app below.
          </p>
          <BaseInput
            v-model="mfaVerificationCode"
            label="Verification Code"
            required
          />
        </div>
      </div>

      <div v-if="mfaStep === 'backup_codes'" class="space-y-6">
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Backup Codes</h3>
          <p class="text-sm text-gray-600 mb-4">
            Save these backup codes in a safe place. You can use them to access your account if you lose your authenticator device.
          </p>
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div class="grid grid-cols-2 gap-2 text-sm font-mono">
              <div v-for="code in mfaBackupCodes" :key="code" class="text-center">
                {{ code }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <BaseButton variant="outline" @click="cancelMFASetup" :disabled="mfaLoading">
            Cancel
          </BaseButton>
          <BaseButton 
            v-if="mfaStep === 'verify_password'"
            variant="primary"
            :loading="mfaLoading"
            @click="handleEnableMfa"
          >
            Continue
          </BaseButton>
          <BaseButton 
            v-if="mfaStep === 'scan_qr'"
            variant="primary"
            :loading="mfaLoading"
            @click="handleVerifyMfa"
          >
            Verify & Enable
          </BaseButton>
          <BaseButton 
            v-if="mfaStep === 'backup_codes'"
            variant="primary"
            @click="closeMFASetup"
          >
            Done
          </BaseButton>
        </div>
      </template>
    </BaseModal>

    <!-- Disable MFA Modal -->
    <BaseModal
      v-model:show="showDisableMFAModal"
      title="Disable Two-Factor Authentication"
      size="md"
    >
      <div class="space-y-4">
        <p class="text-sm text-gray-600">
          To disable 2FA, please enter your password and a code from your authenticator app.
        </p>
        <BaseInput
          v-model="disableMfaForm.password"
          label="Current Password"
          type="password"
          required
          :error="mfaErrors.password"
        />
        <BaseInput
          v-model="disableMfaForm.mfa_code"
          label="Authenticator Code"
          required
        />
      </div>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <BaseButton variant="outline" @click="showDisableMFAModal = false" :disabled="mfaLoading">
            Cancel
          </BaseButton>
          <BaseButton 
            variant="danger"
            :loading="mfaLoading"
            @click="confirmDisableMfa"
            :disabled="!disableMfaForm.password || !disableMfaForm.mfa_code"
          >
            Disable MFA
          </BaseButton>
        </div>
      </template>
    </BaseModal>

    <!-- Success/Error Notifications -->
    <div 
      v-if="notification.show"
      :class="[
        'fixed top-4 right-4 z-50 max-w-md w-full',
        'transform transition-all duration-300 ease-in-out',
        notification.show ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      ]"
    >
      <BaseAlert
        :variant="notification.type"
        :title="notification.title"
        :message="notification.message"
        @close="hideNotification"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import userService from '@/services/user'
import authService from '@/services/auth'
import { BaseButton, BaseInput, BaseModal, BaseAlert, TheSidebar } from '@/components/ui'
import { CalendarIcon, Bars3Icon } from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const sidebarOpen = ref(false)

// Notification state
const notification = reactive({
  show: false,
  type: 'success' as 'success' | 'danger',
  title: '',
  message: ''
})

// Profile form
const profileForm = reactive({
  full_name: '',
  email: ''
})
const profileErrors = reactive({
  full_name: '',
  email: ''
})
const profileLoading = ref(false)

// Password form
const passwordForm = reactive({
  current_password: '',
  new_password: ''
})
const passwordErrors = reactive({
  current_password: '',
  new_password: ''
})
const passwordLoading = ref(false)

// MFA state
const mfaLoading = ref(false)
const showMFASetupModal = ref(false)
const showDisableMFAModal = ref(false)
const mfaStep = ref<'verify_password' | 'scan_qr' | 'backup_codes'>('verify_password')
const mfaPassword = ref('')
const mfaQRCode = ref('')
const mfaSecret = ref('')
const mfaVerificationCode = ref('')
const mfaBackupCodes = ref<string[]>([])
const disableMfaForm = reactive({
  password: '',
  mfa_code: ''
})
const mfaErrors = reactive({
  password: '',
  verificationCode: ''
})

// Methods
onMounted(() => {
  if (user.value) {
    profileForm.full_name = user.value.full_name
    profileForm.email = user.value.email
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const showNotification = (type: 'success' | 'danger', title: string, message: string) => {
  notification.type = type
  notification.title = title
  notification.message = message
  notification.show = true
  setTimeout(() => {
    hideNotification()
  }, 5000)
}

const hideNotification = () => {
  notification.show = false
}

// Profile update logic
const handleUpdateProfile = async () => {
  profileLoading.value = true
  profileErrors.full_name = ''
  profileErrors.email = ''
  try {
    await userService.updateProfile({
      full_name: profileForm.full_name,
      email: profileForm.email
    })
    showNotification('success', 'Profile Updated', 'Your profile information has been successfully updated.')
    // Refresh user data in store
    await authStore.fetchUser()
  } catch (error: unknown) {
    if (error instanceof Error && 'response' in error) {
      const err = error as { response?: { data?: { detail?: string | any[] } } }
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        detail.forEach((e: any) => {
          if (e.loc.includes('full_name')) profileErrors.full_name = e.msg
          if (e.loc.includes('email')) profileErrors.email = e.msg
        })
      } else {
        showNotification('danger', 'Update Failed', detail || 'An unknown error occurred.')
      }
    } else {
      showNotification('danger', 'Update Failed', 'An unknown error occurred.')
    }
  } finally {
    profileLoading.value = false
  }
}

// Password change logic
const handleChangePassword = async () => {
  passwordLoading.value = true
  passwordErrors.current_password = ''
  passwordErrors.new_password = ''
  try {
    await userService.changePassword({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password
    })
    showNotification('success', 'Password Changed', 'Your password has been changed successfully.')
    passwordForm.current_password = ''
    passwordForm.new_password = ''
  } catch (error: unknown) {
    if (error instanceof Error && 'response' in error) {
      const err = error as { response?: { data?: { detail?: string } } }
      showNotification('danger', 'Change Failed', err.response?.data?.detail || 'Failed to change password.')
    } else {
      showNotification('danger', 'Change Failed', 'An unknown error occurred.')
    }
  } finally {
    passwordLoading.value = false
  }
}

// MFA logic
const cancelMFASetup = () => {
  showMFASetupModal.value = false
  mfaStep.value = 'verify_password'
  mfaPassword.value = ''
  mfaVerificationCode.value = ''
}

const closeMFASetup = () => {
  showMFASetupModal.value = false
}

const handleEnableMfa = async () => {
  mfaLoading.value = true
  try {
    const response = await authService.enableMFA(mfaPassword.value)
    mfaQRCode.value = response.qr_code
    mfaSecret.value = response.secret
    mfaStep.value = 'scan_qr'
  } catch (error: unknown) {
    if (error instanceof Error && 'response' in error) {
      const err = error as { response?: { data?: { detail?: string } } }
      showNotification('danger', 'MFA Setup Failed', err.response?.data?.detail || 'Could not initiate MFA setup.')
    } else {
      showNotification('danger', 'MFA Setup Failed', 'An unknown error occurred.')
    }
  } finally {
    mfaLoading.value = false
  }
}

const handleVerifyMfa = async () => {
  mfaLoading.value = true
  try {
    const response = await authService.verifyMFASetup(mfaVerificationCode.value)
    mfaBackupCodes.value = response.backup_codes
    mfaStep.value = 'backup_codes'
    await authStore.fetchUser() // Refresh user data
  } catch (error: unknown) {
    if (error instanceof Error && 'response' in error) {
      const err = error as { response?: { data?: { detail?: string } } }
      showNotification('danger', 'Verification Failed', err.response?.data?.detail || 'Invalid verification code.')
    } else {
      showNotification('danger', 'Verification Failed', 'An unknown error occurred.')
    }
  } finally {
    mfaLoading.value = false
  }
}

const confirmDisableMfa = async () => {
  mfaLoading.value = true
  mfaErrors.password = ''
  try {
    await authService.disableMFA(disableMfaForm.password, disableMfaForm.mfa_code)
    showNotification('success', 'MFA Disabled', 'Two-factor authentication has been disabled.')
    showDisableMFAModal.value = false
    await authStore.fetchUser()
  } catch (error: unknown) {
    if (error instanceof Error && 'response' in error) {
      const err = error as { response?: { data?: { detail?: string } } }
      showNotification('danger', 'Disabling MFA Failed', err.response?.data?.detail || 'An error occurred.')
    } else {
      showNotification('danger', 'Disabling MFA Failed', 'An unknown error occurred.')
    }
  } finally {
    mfaLoading.value = false
    disableMfaForm.password = ''
    disableMfaForm.mfa_code = ''
  }
}
</script> 