<template>
  <TabGroup
    :selectedIndex="selectedIndex"
    @change="handleChange"
    :vertical="vertical"
    as="div"
    :class="containerClasses"
  >
    <TabList :class="tabListClasses">
      <Tab
        v-for="(tab, index) in tabs"
        :key="index"
        :class="tabClasses(index === (selectedIndex ?? 0))"
        :disabled="tab.disabled"
      >
        {{ tab.label }}
      </Tab>
    </TabList>

    <TabPanels :class="panelsClasses">
      <TabPanel
        v-for="(tab, index) in tabs"
        :key="index"
        :class="panelClasses"
      >
        <slot :name="`panel-${index}`" :tab="tab" :index="index">
          <div v-if="tab.content" v-html="tab.content" />
        </slot>
      </TabPanel>
    </TabPanels>
  </TabGroup>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { TabGroup, TabList, Tab, TabPanels, TabPanel } from '@headlessui/vue'

interface TabItem {
  label: string
  content?: string
  disabled?: boolean
  [key: string]: any
}

const props = defineProps<{
  tabs: TabItem[]
  selectedIndex?: number
  variant?: 'default' | 'pills' | 'underline'
  size?: 'sm' | 'md' | 'lg'
  vertical?: boolean
  fullWidth?: boolean
}>()

const emit = defineEmits(['change'])

const handleChange = (index: number) => {
  emit('change', index)
}

const containerClasses = computed(() => {
  if (props.vertical) {
    return 'flex space-x-4'
  }
  return 'space-y-4'
})

const tabListClasses = computed(() => {
  const baseClasses = 'flex'

  if (props.vertical) {
    return `${baseClasses} flex-col space-y-1 min-w-max`
  }

  const variantClasses: Record<string, string> = {
    default: 'border-b border-gray-200',
    pills: 'bg-gray-100 p-1 rounded-lg',
    underline: 'border-b border-gray-200'
  }

  const widthClasses = props.fullWidth ? 'w-full' : ''

  return [
    baseClasses,
    variantClasses[props.variant || 'default'],
    widthClasses,
    props.vertical ? '' : 'space-x-1'
  ].filter(Boolean).join(' ')
})

const tabClasses = (selected: boolean) => {
  const sizeClasses: Record<string, string> = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }

  const baseClasses = [
    'font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500',
    sizeClasses[props.size || 'md']
  ]

  if (props.fullWidth && !props.vertical) {
    baseClasses.push('flex-1')
  }

  // Variant-specific styling
  const variantClasses: Record<string, { base: string; selected: string; unselected: string }> = {
    default: {
      base: 'border-b-2 border-transparent hover:text-gray-700 hover:border-gray-300',
      selected: 'text-primary-600 border-primary-500',
      unselected: 'text-gray-500'
    },
    pills: {
      base: 'rounded-md hover:bg-white hover:shadow-sm',
      selected: 'bg-white text-primary-600 shadow-sm',
      unselected: 'text-gray-600'
    },
    underline: {
      base: 'border-b-2 border-transparent hover:text-gray-700',
      selected: 'text-primary-600 border-primary-500',
      unselected: 'text-gray-500'
    }
  }

  const variant = variantClasses[props.variant || 'default']

  return [
    ...baseClasses,
    variant.base,
    selected ? variant.selected : variant.unselected
  ].join(' ')
}

const panelsClasses = computed(() => {
  if (props.vertical) {
    return 'flex-1'
  }
  return 'mt-4'
})

const panelClasses = computed(() => {
  return 'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 rounded-md'
})
</script>


