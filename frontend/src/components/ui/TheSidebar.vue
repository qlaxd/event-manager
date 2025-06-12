<template>
  <!-- Mobile Sidebar Overlay -->
  <div
    v-if="isOpen && isMobile"
    class="fixed inset-0 z-40 lg:hidden"
    @click="$emit('close')"
  >
    <div class="fixed inset-0 bg-gray-600 bg-opacity-75"></div>
  </div>

  <!-- Sidebar -->
  <aside 
    :class="[
      'bg-white shadow-lg flex flex-col transition-transform duration-300 ease-in-out',
      'fixed inset-y-0 left-0 z-50 w-64 lg:static lg:inset-0 lg:translate-x-0',
      isOpen || !isMobile ? 'translate-x-0' : '-translate-x-full'
    ]"
  >
    <!-- Logo/Brand -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <div class="flex items-center justify-center w-8 h-8 bg-gray-900 text-white rounded-lg">
            <CalendarIcon class="w-5 h-5" />
          </div>
          <h1 class="ml-3 text-xl font-bold text-gray-900">EventManager</h1>
        </div>
        <!-- Close button for mobile -->
        <button
          @click="$emit('close')"
          class="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
        >
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
      <RouterLink
        v-for="item in navigationItems"
        :key="item.name"
        :to="item.to"
        :class="[
          'flex items-center px-3 py-2 text-sm font-medium rounded-lg',
          isActiveRoute(item.to) 
            ? 'bg-gray-900 text-white' 
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
        ]"
        @click="handleNavClick"
      >
        <component :is="item.icon" class="w-5 h-5 mr-3 flex-shrink-0" />
        <span class="truncate">{{ item.name }}</span>
      </RouterLink>
    </nav>

    <!-- User Menu -->
    <div class="px-4 py-4 border-t border-gray-200">
      <Menu as="div" class="relative">
        <MenuButton class="flex items-center w-full px-3 py-2 text-sm text-gray-600 rounded-lg hover:bg-gray-100">
          <UserCircleIcon class="w-8 h-8 mr-3 flex-shrink-0" />
          <div class="text-left min-w-0 flex-1">
            <p class="text-sm font-medium text-gray-900 truncate">{{ user?.full_name || 'User' }}</p>
            <p class="text-xs text-gray-500 truncate">{{ user?.email || 'user@example.com' }}</p>
          </div>
          <ChevronUpDownIcon class="w-4 h-4 ml-2 flex-shrink-0" />
        </MenuButton>
        <transition
          enter-active-class="transition duration-100 ease-out"
          enter-from-class="transform scale-95 opacity-0"
          enter-to-class="transform scale-100 opacity-100"
          leave-active-class="transition duration-75 ease-in"
          leave-from-class="transform scale-100 opacity-100"
          leave-to-class="transform scale-95 opacity-0"
        >
          <MenuItems class="absolute bottom-full left-0 w-full mb-1 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
            <MenuItem v-slot="{ active }">
              <RouterLink
                to="/profile"
                :class="[
                  active ? 'bg-gray-100' : '',
                  'flex items-center px-3 py-2 text-sm text-gray-700'
                ]"
                @click="handleNavClick"
              >
                <UserIcon class="w-4 h-4 mr-2" />
                Profile
              </RouterLink>
            </MenuItem>
            <MenuItem v-slot="{ active }">
              <button
                @click="handleLogout"
                :class="[
                  active ? 'bg-gray-100' : '',
                  'flex items-center w-full px-3 py-2 text-sm text-gray-700'
                ]"
              >
                <ArrowRightOnRectangleIcon class="w-4 h-4 mr-2" />
                Sign out
              </button>
            </MenuItem>
          </MenuItems>
        </transition>
      </Menu>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, type Component } from 'vue'
import { useRoute } from 'vue-router'
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'
import {
  CalendarIcon,
  CalendarDaysIcon,
  HomeIcon,
  PlusIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  UserCircleIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  ChevronUpDownIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import { RouterLink } from 'vue-router'

interface User {
  full_name?: string
  email?: string
}

interface NavigationItem {
  name: string
  to: string
  icon: Component
}

interface Props {
  user?: User | null
  navigationItems?: NavigationItem[]
  isOpen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  user: null,
  isOpen: false,
  navigationItems: () => [
    {
      name: 'Dashboard',
      to: '/dashboard',
      icon: HomeIcon
    },
    {
      name: 'My Events',
      to: '/events',
      icon: CalendarDaysIcon
    },
    {
      name: 'Create Event',
      to: '/events/create',
      icon: PlusIcon
    },
    {
      name: 'Analytics',
      to: '/analytics',
      icon: ChartBarIcon
    },
    {
      name: 'Settings',
      to: '/settings',
      icon: Cog6ToothIcon
    }
  ]
})

const emit = defineEmits<{
  logout: []
  close: []
}>()

const route = useRoute()
const isMobile = ref(false)

const isActiveRoute = (path: string) => {
  return route.path === path
}

const handleNavClick = () => {
  if (isMobile.value) {
    emit('close')
  }
}

const handleLogout = () => {
  emit('logout')
  if (isMobile.value) {
    emit('close')
  }
}

const checkMobile = () => {
  isMobile.value = window.innerWidth < 1024 // lg breakpoint
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script> 