// Export all UI components for easy importing
export { default as BaseButton } from './BaseButton.vue'
export { default as BaseInput } from './BaseInput.vue'
export { default as BaseModal } from './BaseModal.vue'
export { default as BaseDropdown } from './BaseDropdown.vue'
export { default as DropdownItem } from './DropdownItem.vue'
export { default as BaseTabs } from './BaseTabs.vue'
export { default as BaseAccordion } from './BaseAccordion.vue'
export { default as BaseAlert } from './BaseAlert.vue'
export { default as TheSidebar } from './TheSidebar.vue'

// Re-export Headless UI components for convenience
export {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionRoot,
  TransitionChild,
  Menu,
  MenuButton,
  MenuItems,
  MenuItem,
  TabGroup,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
  Popover,
  PopoverButton,
  PopoverPanel,
} from '@headlessui/vue' 