<template>
  <Menu as="div" class="relative inline-block text-left">
    <div>
      <MenuButton :class="triggerClasses" @click="handleToggle">
        <slot name="trigger">
          <span>{{ triggerText }}</span>
          <svg 
            class="ml-2 -mr-1 h-5 w-5 transition-transform"
            :class="{ 'rotate-180': open }"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </slot>
      </MenuButton>
    </div>

    <transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <MenuItems :class="menuClasses">
        <div class="py-1">
          <slot />
        </div>
      </MenuItems>
    </transition>
  </Menu>
</template>

<script setup>
import { computed } from 'vue'
import { Menu, MenuButton, MenuItems } from '@headlessui/vue'

const props = defineProps({
  triggerText: {
    type: String,
    default: 'Options'
  },
  position: {
    type: String,
    default: 'bottom-right',
    validator: (value) => [
      'bottom-left', 'bottom-right', 'top-left', 'top-right',
      'left', 'right'
    ].includes(value)
  },
  triggerVariant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'ghost', 'outline'].includes(value)
  },
  width: {
    type: String,
    default: 'auto',
    validator: (value) => ['auto', 'trigger', 'sm', 'md', 'lg'].includes(value)
  }
})

const emit = defineEmits(['toggle'])

const handleToggle = () => {
  emit('toggle')
}

const triggerClasses = computed(() => {
  const baseClasses = 'inline-flex w-full justify-center items-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2'
  
  const variants = {
    default: 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300 focus:ring-primary-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    outline: 'border border-gray-300 text-gray-700 bg-transparent hover:bg-gray-50 focus:ring-primary-500'
  }
  
  return [baseClasses, variants[props.triggerVariant] || variants.default].join(' ')
})

const menuClasses = computed(() => {
  const baseClasses = 'absolute z-10 bg-white divide-y divide-gray-100 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none'
  
  // Position classes
  const positionClasses = {
    'bottom-left': 'left-0 mt-2 origin-top-left',
    'bottom-right': 'right-0 mt-2 origin-top-right',
    'top-left': 'left-0 bottom-full mb-2 origin-bottom-left',
    'top-right': 'right-0 bottom-full mb-2 origin-bottom-right',
    'left': 'right-full mr-2 top-0 origin-top-right',
    'right': 'left-full ml-2 top-0 origin-top-left'
  }
  
  // Width classes
  const widthClasses = {
    auto: 'min-w-max',
    trigger: 'w-full',
    sm: 'w-48',
    md: 'w-56',
    lg: 'w-64'
  }
  
  return [
    baseClasses,
    positionClasses[props.position] || positionClasses['bottom-right'],
    widthClasses[props.width] || widthClasses.auto
  ].join(' ')
})
</script> 

<!-- bump -->
