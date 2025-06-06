<template>
  <TransitionRoot appear :show="true" as="template">
    <Dialog as="div" @close="handleClose" class="relative z-50">
      <!-- Backdrop -->
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                Two-Factor Authentication
              </DialogTitle>
              
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  Enter the 6-digit code from your authenticator app
                </p>
              </div>

              <form @submit.prevent="handleSubmit" class="mt-4">
                <!-- TOTP Code Input -->
                <div class="mt-4">
                  <label for="totp-code" class="sr-only">Verification code</label>
                  <div class="flex justify-between space-x-2">
                    <input
                      v-for="(digit, index) in digits"
                      :key="index"
                      :ref="(el) => (digitRefs[index] = el as HTMLInputElement)"
                      v-model="digits[index]"
                      type="text"
                      maxlength="1"
                      class="w-12 h-12 text-center text-lg font-semibold border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      :class="{ 'border-red-500': error }"
                      @input="handleInput(index, $event)"
                      @keydown="handleKeydown(index, $event)"
                      @paste="handlePaste"
                      inputmode="numeric"
                      pattern="[0-9]"
                    />
                  </div>
                </div>

                <!-- Error Message -->
                <Transition
                  enter-active-class="transition ease-out duration-200"
                  enter-from-class="transform opacity-0 scale-95"
                  enter-to-class="transform opacity-100 scale-100"
                  leave-active-class="transition ease-in duration-150"
                  leave-from-class="transform opacity-100 scale-100"
                  leave-to-class="transform opacity-0 scale-95"
                >
                  <p v-if="error" class="mt-2 text-sm text-red-600">
                    {{ error }}
                  </p>
                </Transition>

                <!-- Actions -->
                <div class="mt-6 flex space-x-3">
                  <button
                    type="button"
                    class="flex-1 btn-secondary"
                    @click="handleClose"
                    :disabled="loading"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    class="flex-1 btn-primary"
                    :disabled="loading || !isCodeComplete"
                  >
                    <span v-if="!loading">Verify</span>
                    <span v-else class="flex items-center justify-center">
                      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Verifying...
                    </span>
                  </button>
                </div>

                <!-- Help Text -->
                <div class="mt-4 text-center">
                  <button
                    type="button"
                    class="text-sm text-primary-600 hover:text-primary-500"
                    @click="showBackupCode = !showBackupCode"
                  >
                    Use backup code instead
                  </button>
                </div>

                <!-- Backup Code Input (Hidden by default) -->
                <Transition
                  enter-active-class="transition ease-out duration-200"
                  enter-from-class="transform opacity-0"
                  enter-to-class="transform opacity-100"
                  leave-active-class="transition ease-in duration-150"
                  leave-from-class="transform opacity-100"
                  leave-to-class="transform opacity-0"
                >
                  <div v-if="showBackupCode" class="mt-4">
                    <label for="backup-code" class="form-label">Backup code</label>
                    <input
                      id="backup-code"
                      v-model="backupCode"
                      type="text"
                      class="form-input"
                      placeholder="Enter your backup code"
                    />
                  </div>
                </Transition>
              </form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
  DialogTitle,
} from '@headlessui/vue'

const props = defineProps<{
  loading?: boolean
  error?: string
}>()

const emit = defineEmits<{
  verify: [code: string]
  close: []
}>()

// State
const digits = ref(['', '', '', '', '', ''])
const digitRefs = ref<HTMLInputElement[]>([])
const showBackupCode = ref(false)
const backupCode = ref('')

// Computed
const code = computed(() => digits.value.join(''))
const isCodeComplete = computed(() => code.value.length === 6 || backupCode.value.length > 0)

// Methods
const handleInput = (index: number, event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value

  // Only allow digits
  if (!/^\d*$/.test(value)) {
    digits.value[index] = ''
    return
  }

  // Move to next input if value entered
  if (value && index < 5) {
    digitRefs.value[index + 1]?.focus()
  }
}

const handleKeydown = (index: number, event: KeyboardEvent) => {
  // Handle backspace
  if (event.key === 'Backspace' && !digits.value[index] && index > 0) {
    digitRefs.value[index - 1]?.focus()
  }

  // Handle arrow keys
  if (event.key === 'ArrowLeft' && index > 0) {
    event.preventDefault()
    digitRefs.value[index - 1]?.focus()
  } else if (event.key === 'ArrowRight' && index < 5) {
    event.preventDefault()
    digitRefs.value[index + 1]?.focus()
  }
}

const handlePaste = (event: ClipboardEvent) => {
  event.preventDefault()
  const pastedData = event.clipboardData?.getData('text') || ''
  const pastedDigits = pastedData.replace(/\D/g, '').slice(0, 6).split('')

  pastedDigits.forEach((digit, index) => {
    if (index < 6) {
      digits.value[index] = digit
    }
  })

  // Focus last filled input or last input
  const lastFilledIndex = Math.min(pastedDigits.length - 1, 5)
  digitRefs.value[lastFilledIndex]?.focus()
}

const handleSubmit = () => {
  if (showBackupCode.value && backupCode.value) {
    emit('verify', backupCode.value)
  } else if (isCodeComplete.value) {
    emit('verify', code.value)
  }
}

const handleClose = () => {
  if (!props.loading) {
    emit('close')
  }
}

// Reset error when code changes
watch([code, backupCode], () => {
  if (props.error) {
    // Parent should clear error
  }
})

// Focus first input on mount
onMounted(() => {
  digitRefs.value[0]?.focus()
})
</script> 

 
