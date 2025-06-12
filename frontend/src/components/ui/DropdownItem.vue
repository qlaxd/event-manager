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
      <span class="flex-1">
        <template v-if="$slots.default">
          <slot />
        </template>
        <template v-else>
          {{ text }}
        </template>
      </span>
      <slot name="shortcut" />
    </component>
  </MenuItem>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MenuItem } from '@headlessui/vue'
import { RouterLink } from 'vue-router'

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
    validator: (value: string) => ['default', 'danger'].includes(value)
  }
})

const emit = defineEmits(['click'])

const component = computed(() => {
  if (props.to) return 'RouterLink'
  if (props.href) return 'a'
  return 'button'
})

const itemDisabled = computed(() => props.disabled)

const handleClick = (event: MouseEvent) => {
  if (!props.disabled) {
    emit('click', event)
  }
}

type Variant = 'default' | 'danger'

const itemClasses = (active: boolean, disabled: boolean) => {
  const baseClasses = 'group flex items-center w-full px-4 py-2 text-sm transition-colors'

  // Variant-specific classes
  const variantClasses: Record<Variant, { normal: string; active: string; disabled: string }> = {
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

  const variant = variantClasses[props.variant as Variant] || variantClasses.default

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


