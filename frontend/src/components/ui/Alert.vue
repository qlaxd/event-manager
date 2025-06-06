<template>
  <Transition
    enter-active-class="transition ease-out duration-300"
    enter-from-class="transform opacity-0 scale-95"
    enter-to-class="transform opacity-100 scale-100"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="transform opacity-100 scale-100"
    leave-to-class="transform opacity-0 scale-95"
  >
    <div v-if="visible" :class="alertClasses">
      <div class="flex">
        <!-- Icon -->
        <div class="flex-shrink-0">
          <slot name="icon">
            <component :is="iconComponent" :class="iconClasses" />
          </slot>
        </div>

        <!-- Content -->
        <div class="ml-3 flex-1">
          <h3 v-if="title" :class="titleClasses">
            {{ title }}
          </h3>
          <div :class="messageClasses">
            <slot>
              <p>{{ message }}</p>
            </slot>
          </div>
          
          <!-- Actions -->
          <div v-if="$slots.actions" class="mt-4">
            <div class="flex">
              <slot name="actions" />
            </div>
          </div>
        </div>

        <!-- Close Button -->
        <div v-if="dismissible" class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button
              type="button"
              :class="closeButtonClasses"
              @click="handleDismiss"
            >
              <span class="sr-only">Dismiss</span>
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'warning', 'error', 'info'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    default: ''
  },
  dismissible: {
    type: Boolean,
    default: true
  },
  show: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['dismiss'])

const visible = ref(props.show)

const handleDismiss = () => {
  visible.value = false
  emit('dismiss')
}

// Icon components as strings for dynamic rendering
const iconComponent = computed(() => {
  const icons = {
    success: 'CheckCircleIcon',
    warning: 'ExclamationTriangleIcon', 
    error: 'XCircleIcon',
    info: 'InformationCircleIcon'
  }
  
  // Return SVG directly since we don't have Heroicons
  return 'svg'
})

const alertClasses = computed(() => {
  const variants = {
    success: 'bg-green-50 border-green-200',
    warning: 'bg-yellow-50 border-yellow-200', 
    error: 'bg-red-50 border-red-200',
    info: 'bg-blue-50 border-blue-200'
  }
  
  return [
    'rounded-md border p-4',
    variants[props.variant] || variants.info
  ].join(' ')
})

const iconClasses = computed(() => {
  const variants = {
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400', 
    info: 'text-blue-400'
  }
  
  return [
    'h-5 w-5',
    variants[props.variant] || variants.info
  ].join(' ')
})

const titleClasses = computed(() => {
  const variants = {
    success: 'text-green-800',
    warning: 'text-yellow-800',
    error: 'text-red-800',
    info: 'text-blue-800'
  }
  
  return [
    'text-sm font-medium',
    variants[props.variant] || variants.info
  ].join(' ')
})

const messageClasses = computed(() => {
  const variants = {
    success: 'text-green-700',
    warning: 'text-yellow-700', 
    error: 'text-red-700',
    info: 'text-blue-700'
  }
  
  const marginClass = props.title ? 'mt-1' : ''
  
  return [
    'text-sm',
    marginClass,
    variants[props.variant] || variants.info
  ].join(' ')
})

const closeButtonClasses = computed(() => {
  const variants = {
    success: 'text-green-400 hover:text-green-600 focus:ring-green-600',
    warning: 'text-yellow-400 hover:text-yellow-600 focus:ring-yellow-600',
    error: 'text-red-400 hover:text-red-600 focus:ring-red-600', 
    info: 'text-blue-400 hover:text-blue-600 focus:ring-blue-600'
  }
  
  return [
    'inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2',
    variants[props.variant] || variants.info
  ].join(' ')
})
</script> 

<!-- bump -->
