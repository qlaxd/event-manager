<template>
  <div class="space-y-2">
    <Disclosure
      v-for="(item, index) in items"
      :key="index"
      v-slot="{ open }"
      :defaultOpen="item.defaultOpen"
      as="div"
      :class="itemClasses"
    >
      <DisclosureButton :class="buttonClasses(open)">
        <slot :name="`button-${index}`" :item="item" :index="index" :open="open">
          <span class="font-medium text-left">{{ item.title }}</span>
        </slot>
        <svg
          :class="iconClasses(open)"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </DisclosureButton>

      <transition
        enter-active-class="transition duration-100 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-75 ease-out"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <DisclosurePanel :class="panelClasses">
          <slot :name="`panel-${index}`" :item="item" :index="index">
            <div v-if="item.content" v-html="item.content" />
          </slot>
        </DisclosurePanel>
      </transition>
    </Disclosure>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
    validator: (items) => items.every(item => 
      typeof item === 'object' && 
      typeof item.title === 'string'
    )
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'bordered', 'flush'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const itemClasses = computed(() => {
  const variants = {
    default: 'bg-white rounded-lg shadow-sm',
    bordered: 'border border-gray-200 rounded-lg',
    flush: ''
  }
  
  return variants[props.variant] || variants.default
})

const buttonClasses = (open) => {
  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-sm',
    lg: 'px-6 py-4 text-base'
  }
  
  const baseClasses = [
    'flex w-full items-center justify-between text-left transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500',
    sizeClasses[props.size] || sizeClasses.md
  ]
  
  const variants = {
    default: 'hover:bg-gray-50 rounded-lg',
    bordered: 'hover:bg-gray-50 rounded-t-lg',
    flush: 'hover:bg-gray-50 border-b border-gray-200'
  }
  
  const openClasses = {
    default: open ? 'bg-gray-50' : '',
    bordered: open ? 'bg-gray-50 border-b border-gray-200' : '',
    flush: ''
  }
  
  return [
    ...baseClasses,
    variants[props.variant] || variants.default,
    openClasses[props.variant] || openClasses.default
  ].filter(Boolean).join(' ')
}

const iconClasses = (open) => {
  return [
    'h-5 w-5 transition-transform duration-200',
    open ? 'rotate-180' : '',
    'text-gray-500'
  ].filter(Boolean).join(' ')
}

const panelClasses = computed(() => {
  const sizeClasses = {
    sm: 'px-3 pb-2',
    md: 'px-4 pb-3',
    lg: 'px-6 pb-4'
  }
  
  const variants = {
    default: 'text-gray-700',
    bordered: 'text-gray-700 border-t border-gray-200',
    flush: 'text-gray-700'
  }
  
  return [
    sizeClasses[props.size] || sizeClasses.md,
    variants[props.variant] || variants.default
  ].join(' ')
})
</script> 

<!-- bump -->
