<template>
  <MenuItem v-slot="{ active, disabled }" :disabled="itemDisabled">
    <component
      :is="component"
      :to="to"
      :href="href"
      :class="itemClasses(active, disabled)"
      @click="handleClick"
    >
      <slot name="icon" />
      <span class="flex-1">{{ text || $slots.default?.[0]?.children }}</span>
      <slot />
      <slot name="shortcut" />
    </component>
  </MenuItem>
</template>

<script setup>
import { computed } from 'vue'
import { MenuItem } from '@headlessui/vue'

const props = defineProps({
  text: {
    type: String,
    default: ''
  },
  href: {
    type: String,
    default: ''
  },
  to: {
    type: [String, Object],
    default: null
  },
  disabled: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'danger'].includes(value)
  }
})

const emit = defineEmits(['click'])

const component = computed(() => {
  if (props.to) return 'RouterLink'
  if (props.href) return 'a'
  return 'button'
})

const itemDisabled = computed(() => props.disabled)

const handleClick = (event) => {
  if (!props.disabled) {
    emit('click', event)
  }
}

const itemClasses = (active, disabled) => {
  const baseClasses = 'group flex items-center w-full px-4 py-2 text-sm transition-colors'
  
  // Variant-specific classes
  const variantClasses = {
    default: {
      normal: 'text-gray-700',
      active: 'bg-gray-100 text-gray-900',
      disabled: 'text-gray-400 cursor-not-allowed'
    },
    danger: {
      normal: 'text-red-700',
      active: 'bg-red-100 text-red-900',
      disabled: 'text-red-400 cursor-not-allowed'
    }
  }
  
  const variant = variantClasses[props.variant] || variantClasses.default
  
  let stateClasses = ''
  if (disabled) {
    stateClasses = variant.disabled
  } else if (active) {
    stateClasses = variant.active
  } else {
    stateClasses = variant.normal
  }
  
  return [baseClasses, stateClasses].join(' ')
}
</script> 

<!-- bump -->
