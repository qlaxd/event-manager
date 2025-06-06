<template>
  <div class="space-y-1">
    <!-- Label -->
    <label 
      v-if="label" 
      :for="inputId" 
      class="form-label"
      :class="{ 'text-red-700': hasError }"
    >
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Input Container -->
    <div class="relative">
      <!-- Left Icon -->
      <div 
        v-if="$slots['icon-left']" 
        class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
      >
        <slot name="icon-left" />
      </div>

      <!-- Input Field -->
      <input
        :id="inputId"
        :type="inputType"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :autocomplete="autocomplete"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @keydown="handleKeydown"
      />

      <!-- Right Icon / Password Toggle -->
      <div 
        v-if="$slots['icon-right'] || (type === 'password')" 
        class="absolute inset-y-0 right-0 pr-3 flex items-center"
      >
        <!-- Password Toggle -->
        <button
          v-if="type === 'password'"
          type="button"
          class="text-gray-400 hover:text-gray-600 focus:outline-none"
          @click="togglePasswordVisibility"
        >
          <svg v-if="!showPassword" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
          </svg>
        </button>

        <!-- Custom Right Icon -->
        <slot v-else name="icon-right" />
      </div>
    </div>

    <!-- Help Text / Error Message -->
    <div class="min-h-[1.25rem]">
      <p v-if="hasError" class="form-error">
        {{ error }}
      </p>
      <p v-else-if="helpText" class="text-sm text-gray-500">
        {{ helpText }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, useSlots } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text',
    validator: (value) => [
      'text', 'email', 'password', 'number', 'tel', 'url', 'search',
      'date', 'datetime-local', 'time', 'month', 'week', 'color',
      'file', 'hidden', 'range'
    ].includes(value)
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  helpText: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  autocomplete: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus', 'keydown'])

// Access slots
const slots = useSlots()

// Generate unique ID for input
const inputId = `input-${Math.random().toString(36).substr(2, 9)}`

// Password visibility toggle
const showPassword = ref(false)

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// Computed properties
const inputType = computed(() => {
  if (props.type === 'password') {
    return showPassword.value ? 'text' : 'password'
  }
  return props.type
})

const hasError = computed(() => {
  return !!props.error
})

const hasLeftIcon = computed(() => {
  return !!slots['icon-left']
})

const hasRightIcon = computed(() => {
  return !!slots['icon-right'] || props.type === 'password'
})

const inputClasses = computed(() => {
  const baseClasses = 'form-input transition-colors'
  
  // Size classes
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  }
  
  // Icon padding
  const leftPadding = hasLeftIcon.value ? 'pl-10' : ''
  const rightPadding = hasRightIcon.value ? 'pr-10' : ''
  
  // Error state
  const errorClasses = hasError.value ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''
  
  // Disabled state
  const disabledClasses = props.disabled ? 'bg-gray-50 cursor-not-allowed' : ''
  
  return [
    baseClasses,
    sizeClasses[props.size] || sizeClasses.md,
    leftPadding,
    rightPadding,
    errorClasses,
    disabledClasses
  ].filter(Boolean).join(' ')
})

// Event handlers
const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleFocus = (event) => {
  emit('focus', event)
}

const handleKeydown = (event) => {
  emit('keydown', event)
}

// Reset password visibility when type changes
watch(() => props.type, () => {
  if (props.type !== 'password') {
    showPassword.value = false
  }
})
</script> 

 
