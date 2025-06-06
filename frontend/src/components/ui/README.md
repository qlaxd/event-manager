# UI Components

A comprehensive set of UI components built with Headless UI Vue and Tailwind CSS.

## Installation

All components are exported from the index file:

```javascript
import { Button, Input, Modal, Dropdown, DropdownItem, Tabs, Accordion, Alert } from '@/components/ui'
```

## Components

### Button

Flexible button component with multiple variants, sizes, and states.

```vue
<template>
  <div class="space-x-4">
    <!-- Basic buttons -->
    <Button variant="primary">Primary</Button>
    <Button variant="secondary">Secondary</Button>
    <Button variant="danger">Danger</Button>
    <Button variant="ghost">Ghost</Button>
    <Button variant="outline">Outline</Button>
    
    <!-- Sizes -->
    <Button size="xs">Extra Small</Button>
    <Button size="sm">Small</Button>
    <Button size="md">Medium</Button>
    <Button size="lg">Large</Button>
    <Button size="xl">Extra Large</Button>
    
    <!-- States -->
    <Button :loading="true" loading-text="Saving...">Save</Button>
    <Button :disabled="true">Disabled</Button>
    
    <!-- With icons -->
    <Button>
      <template #icon-left>
        <svg class="h-4 w-4">...</svg>
      </template>
      With Icon
    </Button>
  </div>
</template>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline'
- `size`: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
- `loading`: boolean
- `disabled`: boolean
- `fullWidth`: boolean

### Input

Form input component with validation, icons, and password toggle.

```vue
<template>
  <div class="space-y-4">
    <!-- Basic input -->
    <Input
      v-model="email"
      type="email"
      label="Email"
      placeholder="Enter your email"
      help-text="We'll never share your email"
    />
    
    <!-- With validation -->
    <Input
      v-model="password"
      type="password"
      label="Password"
      :error="passwordError"
      required
    />
    
    <!-- With icons -->
    <Input
      v-model="search"
      placeholder="Search..."
    >
      <template #icon-left>
        <svg class="h-5 w-5 text-gray-400">...</svg>
      </template>
    </Input>
  </div>
</template>
```

**Props:**
- `modelValue`: string | number
- `type`: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'
- `label`: string
- `error`: string
- `helpText`: string
- `required`: boolean
- `disabled`: boolean

### Modal

Modal dialog component with customizable sizes and transitions.

```vue
<template>
  <Modal
    v-model:show="showModal"
    title="Confirm Action"
    size="md"
    @close="handleClose"
  >
    <p>Are you sure you want to delete this item?</p>
    
    <template #footer>
      <Button variant="outline" @click="showModal = false">Cancel</Button>
      <Button variant="danger" @click="confirmDelete">Delete</Button>
    </template>
  </Modal>
</template>
```

**Props:**
- `show`: boolean (required)
- `title`: string
- `size`: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'
- `closable`: boolean
- `persistent`: boolean

### Dropdown

Dropdown menu component with flexible positioning.

```vue
<template>
  <Dropdown trigger-text="Options" position="bottom-right">
    <DropdownItem text="Edit" @click="handleEdit" />
    <DropdownItem text="Share" @click="handleShare" />
    <DropdownItem text="Delete" variant="danger" @click="handleDelete" />
  </Dropdown>
</template>
```

**Props (Dropdown):**
- `triggerText`: string
- `position`: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right' | 'left' | 'right'
- `triggerVariant`: 'default' | 'ghost' | 'outline'

**Props (DropdownItem):**
- `text`: string
- `href`: string
- `to`: string | object (for Vue Router)
- `disabled`: boolean
- `variant`: 'default' | 'danger'

### Tabs

Tab component with multiple variants and orientations.

```vue
<template>
  <Tabs
    :tabs="tabItems"
    variant="pills"
    @change="handleTabChange"
  >
    <template #panel-0>
      <p>Content for tab 1</p>
    </template>
    <template #panel-1>
      <p>Content for tab 2</p>
    </template>
  </Tabs>
</template>

<script setup>
const tabItems = [
  { label: 'Tab 1' },
  { label: 'Tab 2' },
  { label: 'Disabled Tab', disabled: true }
]
</script>
```

**Props:**
- `tabs`: Array (required) - Array of tab objects with `label` property
- `variant`: 'default' | 'pills' | 'underline'
- `size`: 'sm' | 'md' | 'lg'
- `vertical`: boolean
- `fullWidth`: boolean

### Accordion

Collapsible content sections using Headless UI Disclosure.

```vue
<template>
  <Accordion
    :items="accordionItems"
    variant="bordered"
  >
    <template #panel-0="{ item }">
      <p>Custom content for {{ item.title }}</p>
    </template>
  </Accordion>
</template>

<script setup>
const accordionItems = [
  {
    title: 'Question 1',
    content: 'Answer 1',
    defaultOpen: true
  },
  {
    title: 'Question 2', 
    content: 'Answer 2'
  }
]
</script>
```

**Props:**
- `items`: Array (required) - Array of objects with `title` property
- `variant`: 'default' | 'bordered' | 'flush'
- `size`: 'sm' | 'md' | 'lg'

### Alert

Alert component for displaying notifications and messages.

```vue
<template>
  <div class="space-y-4">
    <Alert
      variant="success"
      title="Success!"
      message="Your changes have been saved."
      @dismiss="handleDismiss"
    />
    
    <Alert
      variant="error"
      message="Something went wrong. Please try again."
    >
      <template #actions>
        <Button size="sm" variant="outline">Retry</Button>
      </template>
    </Alert>
  </div>
</template>
```

**Props:**
- `variant`: 'success' | 'warning' | 'error' | 'info'
- `title`: string
- `message`: string
- `dismissible`: boolean
- `show`: boolean

## Global Usage

You can also register these components globally in your main.js:

```javascript
import { createApp } from 'vue'
import App from './App.vue'
import * as UIComponents from '@/components/ui'

const app = createApp(App)

// Register all UI components globally
Object.entries(UIComponents).forEach(([name, component]) => {
  if (component.__name || component.name) {
    app.component(name, component)
  }
})

app.mount('#app')
```

## Customization

All components use Tailwind CSS classes and follow the design system defined in your CSS. You can customize colors by modifying the primary color values in your Tailwind config or CSS variables.

## Accessibility

All components are built with accessibility in mind:
- Proper ARIA attributes
- Keyboard navigation support
- Focus management
- Screen reader friendly
- High contrast support

## TypeScript Support

All components include proper TypeScript definitions and prop validation for better development experience. 