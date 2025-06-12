<template>
  <button
    :type="p.type"
    :disabled="p.disabled || p.loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <span v-if="p.loading" class="flex items-center justify-center">
      <svg
        class="animate-spin mr-2 h-4 w-4"
        :class="loadingIconColor"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {{ p.loadingText || 'Loading...' }}
    </span>
    <span v-else class="flex items-center justify-center">
      <slot name="icon-left" />
      <slot />
      <slot name="icon-right" />
    </span>
  </button>
</template>

<script lang="ts">
import type { PropType } from 'vue'

const variantOptions = ['primary', 'secondary', 'danger', 'ghost', 'outline'] as const
const sizeOptions = ['xs', 'sm', 'md', 'lg', 'xl'] as const
const roundedOptions = ['none', 'sm', 'md', 'lg', 'full'] as const

type Variant = typeof variantOptions[number]
type Size = typeof sizeOptions[number]
type Rounded = typeof roundedOptions[number]
type ButtonType = 'button' | 'submit' | 'reset'

export interface BaseButtonProps {
  variant?: Variant
  size?: Size
  type?: ButtonType
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  fullWidth?: boolean
  rounded?: Rounded
}
</script>

<script setup lang="ts">
import { computed } from 'vue'

// Types are available from the <script lang="ts"> block above
const p = defineProps<BaseButtonProps>()
const emit = defineEmits(['click'])

const handleClick = (event: MouseEvent) => {
  if (!p.disabled && !p.loading) {
    emit('click', event)
  }
}

const baseClasses = 'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'

const variantClasses = computed(() => {
  const variants: Record<Variant, string> = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    outline: 'border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-primary-500'
  }
  return variants[p.variant ?? 'primary']
})

const sizeClasses = computed(() => {
  const sizes: Record<Size, string> = {
    xs: 'px-2.5 py-1.5 text-xs',
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-4 py-2 text-base',
    xl: 'px-6 py-3 text-base'
  }
  return sizes[p.size ?? 'md']
})

const roundedClasses = computed(() => {
  const rounded: Record<Rounded, string> = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full'
  }
  return rounded[p.rounded ?? 'md']
})

const widthClasses = computed(() => {
  return p.fullWidth ? 'w-full' : ''
})

const loadingIconColor = computed(() => {
  return p.variant === 'ghost' || p.variant === 'outline' ? 'text-gray-600' : 'text-white'
})

const buttonClasses = computed(() => {
  return [
    baseClasses,
    variantClasses.value,
    sizeClasses.value,
    roundedClasses.value,
    widthClasses.value
  ].filter(Boolean).join(' ')
})
</script>

