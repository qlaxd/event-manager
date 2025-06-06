<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Main Layout Container -->
    <div class="flex h-screen">
      <!-- Left Sidebar -->
      <Sidebar 
        :user="user" 
        @logout="handleLogout" 
      />

      <!-- Main Content -->
      <div class="flex-1 overflow-y-auto">
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
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
                    <Input
                      v-model="profileForm.full_name"
                      label="Full Name"
                      type="text"
                      required
                      :error="profileErrors.full_name"
                    />
                  </div>
                  <div>
                    <Input
                      v-model="profileForm.email"
                      label="Email Address"
                      type="email"
                      required
                      :error="profileErrors.email"
                    />
                  </div>
                </div>
                <div>
                  <Button 
                    type="submit" 
                    variant="primary"
                    :loading="profileLoading"
                    loading-text="Updating..."
                  >
                    Update Profile
                  </Button>
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
                    <Input
                      v-model="passwordForm.current_password"
                      label="Current Password"
                      type="password"
                      required
                      :error="passwordErrors.current_password"
                    />
                  </div>
                  <div>
                    <Input
                      v-model="passwordForm.new_password"
                      label="New Password"
                      type="password"
                      required
                      :error="passwordErrors.new_password"
                    />
                  </div>
                </div>
                <div>
                  <Button 
                    type="submit" 
                    variant="primary"
                    :loading="passwordLoading"
                    loading-text="Changing..."
                  >
                    Change Password
                  </Button>
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
                  <Button 
                    v-if="!user?.mfa_enabled"
                    variant="primary"
                    :loading="mfaLoading"
                    @click="handleSetupMFA"
                  >
                    Set up MFA
                  </Button>
                  <Button 
                    v-else
                    variant="outline"
                    :loading="mfaLoading"
                    @click="handleDisableMFA"
                  >
                    Disable MFA
                  </Button>
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MFA Setup Modal -->
    <Modal
      v-model:show="showMFASetupModal"
      title="Set up Two-Factor Authentication"
      size="md"
      :closable="!mfaLoading"
    >
      <div v-if="mfaSetupStep === 'setup'" class="space-y-6">
        <div class="text-center">
          <p class="text-sm text-gray-600 mb-4">
            Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
          </p>
          <div class="flex justify-center mb-4">
            <div class="p-4 bg-white border-2 border-gray-300 rounded-lg">
              <img :src="mfaQRCode" alt="MFA QR Code" class="w-48 h-48" />
            </div>
          </div>
          <div class="text-xs text-gray-500 break-all">
            <p>Manual entry key:</p>
            <code class="bg-gray-100 px-2 py-1 rounded">{{ mfaSecret }}</code>
          </div>
        </div>
        
        <div>
          <Input
            v-model="mfaVerificationCode"
            label="Enter verification code"
            placeholder="000000"
            :error="mfaErrors.code"
            maxlength="6"
          />
        </div>
      </div>

      <div v-if="mfaSetupStep === 'backup-codes'" class="space-y-6">
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
        <div v-if="mfaSetupStep === 'setup'" class="flex justify-end space-x-3">
          <Button variant="outline" @click="showMFASetupModal = false" :disabled="mfaLoading">
            Cancel
          </Button>
          <Button 
            variant="primary" 
            :loading="mfaLoading"
            @click="handleVerifyMFASetup"
            :disabled="!mfaVerificationCode || mfaVerificationCode.length !== 6"
          >
            Verify & Enable
          </Button>
        </div>
        <div v-if="mfaSetupStep === 'backup-codes'" class="flex justify-end">
          <Button variant="primary" @click="handleMFASetupComplete">
            I've saved my backup codes
          </Button>
        </div>
      </template>
    </Modal>

    <!-- MFA Disable Modal -->
    <Modal
      v-model:show="showMFADisableModal"
      title="Disable Two-Factor Authentication"
      size="md"
    >
      <div class="space-y-4">
        <p class="text-sm text-gray-600">
          Please enter your password to disable two-factor authentication.
        </p>
        <Input
          v-model="mfaDisablePassword"
          label="Password"
          type="password"
          required
          :error="mfaErrors.password"
        />
      </div>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <Button variant="outline" @click="showMFADisableModal = false" :disabled="mfaLoading">
            Cancel
          </Button>
          <Button 
            variant="danger"
            :loading="mfaLoading"
            @click="handleConfirmDisableMFA"
            :disabled="!mfaDisablePassword"
          >
            Disable MFA
          </Button>
        </div>
      </template>
    </Modal>

    <!-- Success/Error Notifications -->
    <div 
      v-if="notification.show"
      :class="[
        'fixed top-4 right-4 z-50 max-w-md w-full',
        'transform transition-all duration-300 ease-in-out',
        notification.show ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      ]"
    >
      <Alert
        :variant="notification.type"
        :title="notification.title"
        :message="notification.message"
        @close="hideNotification"
      />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import userService from '@/services/user'
import authService from '@/services/auth'
import { Button, Input, Modal, Dropdown, DropdownItem, Alert } from '@/components/ui'
import Sidebar from '@/components/ui/Sidebar.vue'

const router = useRouter()
const authStore = useAuthStore()

// Reactive data
const { user } = authStore

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

// MFA
const mfaLoading = ref(false)
const showMFASetupModal = ref(false)
const showMFADisableModal = ref(false)
const mfaSetupStep = ref<'setup' | 'backup-codes'>('setup')
const mfaQRCode = ref('')
const mfaSecret = ref('')
const mfaBackupCodes = ref<string[]>([])
const mfaVerificationCode = ref('')
const mfaDisablePassword = ref('')

const mfaErrors = reactive({
  code: '',
  password: ''
})

// Notifications
const notification = reactive({
  show: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})

// Initialize form data
onMounted(() => {
  if (user) {
    profileForm.full_name = user.full_name
    profileForm.email = user.email
  }
})

// Methods
const clearProfileErrors = () => {
  profileErrors.full_name = ''
  profileErrors.email = ''
}

const clearPasswordErrors = () => {
  passwordErrors.current_password = ''
  passwordErrors.new_password = ''
}

const clearMFAErrors = () => {
  mfaErrors.code = ''
  mfaErrors.password = ''
}

const showNotification = (type: typeof notification.type, title: string, message: string) => {
  notification.type = type
  notification.title = title
  notification.message = message
  notification.show = true
  
  // Auto hide after 5 seconds
  setTimeout(() => {
    hideNotification()
  }, 5000)
}

const hideNotification = () => {
  notification.show = false
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

const handleUpdateProfile = async () => {
  clearProfileErrors()
  profileLoading.value = true

  try {
    const response = await userService.updateProfile({
      full_name: profileForm.full_name,
      email: profileForm.email
    })

         // Update user in store
     authStore.updateUser(response.user)
    
    showNotification('success', 'Success', 'Profile updated successfully')
  } catch (error: any) {
    console.error('Profile update error:', error)
    
    if (error.response?.data?.errors) {
      const errors = error.response.data.errors
      if (errors.full_name) profileErrors.full_name = errors.full_name[0]
      if (errors.email) profileErrors.email = errors.email[0]
    } else {
      showNotification('error', 'Error', 'Failed to update profile. Please try again.')
    }
  } finally {
    profileLoading.value = false
  }
}

const handleChangePassword = async () => {
  clearPasswordErrors()
  passwordLoading.value = true

  try {
    await userService.changePassword({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password
    })

    // Clear form
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    
    showNotification('success', 'Success', 'Password changed successfully')
  } catch (error: any) {
    console.error('Password change error:', error)
    
    if (error.response?.data?.errors) {
      const errors = error.response.data.errors
      if (errors.current_password) passwordErrors.current_password = errors.current_password[0]
      if (errors.new_password) passwordErrors.new_password = errors.new_password[0]
    } else {
      showNotification('error', 'Error', 'Failed to change password. Please try again.')
    }
  } finally {
    passwordLoading.value = false
  }
}

const handleSetupMFA = async () => {
  mfaLoading.value = true
  clearMFAErrors()

  try {
    const response = await authService.setupMFA()
    
    mfaQRCode.value = response.qr_code
    mfaSecret.value = response.secret
    mfaBackupCodes.value = response.backup_codes
    mfaSetupStep.value = 'setup'
    showMFASetupModal.value = true
  } catch (error: any) {
    console.error('MFA setup error:', error)
    showNotification('error', 'Error', 'Failed to set up MFA. Please try again.')
  } finally {
    mfaLoading.value = false
  }
}

const handleVerifyMFASetup = async () => {
  clearMFAErrors()
  mfaLoading.value = true

  try {
    await authService.verifyMFA(mfaVerificationCode.value)
    
    // Update user MFA status
    if (authStore.user) {
      authStore.user.mfa_enabled = true
    }
    
    mfaSetupStep.value = 'backup-codes'
  } catch (error: any) {
    console.error('MFA verification error:', error)
    mfaErrors.code = 'Invalid verification code'
  } finally {
    mfaLoading.value = false
  }
}

const handleMFASetupComplete = () => {
  showMFASetupModal.value = false
  mfaSetupStep.value = 'setup'
  mfaVerificationCode.value = ''
  showNotification('success', 'Success', 'Two-factor authentication has been enabled')
}

const handleDisableMFA = () => {
  mfaDisablePassword.value = ''
  clearMFAErrors()
  showMFADisableModal.value = true
}

const handleConfirmDisableMFA = async () => {
  clearMFAErrors()
  mfaLoading.value = true

  try {
    await authService.disableMFA(mfaDisablePassword.value)
    
    // Update user MFA status
    if (authStore.user) {
      authStore.user.mfa_enabled = false
    }
    
    showMFADisableModal.value = false
    mfaDisablePassword.value = ''
    showNotification('success', 'Success', 'Two-factor authentication has been disabled')
  } catch (error: any) {
    console.error('MFA disable error:', error)
    mfaErrors.password = 'Invalid password'
  } finally {
    mfaLoading.value = false
  }
}
</script> 