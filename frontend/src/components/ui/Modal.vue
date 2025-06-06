<template>
  <TransitionRoot appear :show="show" as="template">
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
        <div :class="containerClasses">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel :class="panelClasses">
              <!-- Header -->
              <div v-if="$slots.header || title" class="flex items-center justify-between p-6 border-b border-gray-200">
                <div>
                  <DialogTitle v-if="title" as="h3" class="text-lg font-medium leading-6 text-gray-900">
                    {{ title }}
                  </DialogTitle>
                  <slot name="header" />
                </div>
                <button
                  v-if="closable"
                  type="button"
                  class="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 transition-colors"
                  @click="handleClose"
                >
                  <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <!-- Body -->
              <div :class="bodyClasses">
                <slot />
              </div>

              <!-- Footer -->
              <div v-if="$slots.footer" class="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50">
                <slot name="footer" />
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { computed } from 'vue'
import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
  DialogTitle,
} from '@headlessui/vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl', '2xl', 'full'].includes(value)
  },
  closable: {
    type: Boolean,
    default: true
  },
  persistent: {
    type: Boolean,
    default: false
  },
  position: {
    type: String,
    default: 'center',
    validator: (value) => ['center', 'top'].includes(value)
  },
  padding: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close', 'update:show'])

const handleClose = () => {
  if (!props.persistent) {
    emit('close')
    emit('update:show', false)
  }
}

const containerClasses = computed(() => {
  const positionClasses = {
    center: 'flex min-h-full items-center justify-center',
    top: 'flex min-h-full items-start justify-center pt-16'
  }
  
  return [
    'p-4 text-center',
    positionClasses[props.position] || positionClasses.center
  ].join(' ')
})

const panelClasses = computed(() => {
  const sizeClasses = {
    xs: 'max-w-xs',
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    full: 'max-w-full mx-4'
  }

  return [
    'w-full transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all',
    sizeClasses[props.size] || sizeClasses.md
  ].join(' ')
})

const bodyClasses = computed(() => {
  return props.padding ? 'p-6' : ''
})
</script> 

 
