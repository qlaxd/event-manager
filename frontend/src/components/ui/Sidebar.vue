<template>
  <aside class="w-64 bg-white shadow-lg flex flex-col">
    <!-- Logo/Brand -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center">
        <div class="flex items-center justify-center w-8 h-8 bg-gray-900 text-white rounded-lg">
          <CalendarIcon class="w-5 h-5" />
        </div>
        <h1 class="ml-3 text-xl font-bold text-gray-900">EventManager</h1>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="flex-1 px-4 py-6 space-y-2">
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
      >
        <component :is="item.icon" class="w-5 h-5 mr-3" />
        {{ item.name }}
      </RouterLink>
    </nav>

    <!-- User Menu -->
    <div class="px-4 py-4 border-t border-gray-200">
      <Menu as="div" class="relative">
        <MenuButton class="flex items-center w-full px-3 py-2 text-sm text-gray-600 rounded-lg hover:bg-gray-100">
          <UserCircleIcon class="w-8 h-8 mr-3" />
          <div class="text-left">
            <p class="text-sm font-medium text-gray-900">{{ user?.full_name || 'User' }}</p>
            <p class="text-xs text-gray-500">{{ user?.email || 'user@example.com' }}</p>
          </div>
          <ChevronUpDownIcon class="w-4 h-4 ml-auto" />
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
              >
                <UserIcon class="w-4 h-4 mr-2" />
                Profile
              </RouterLink>
            </MenuItem>
            <MenuItem v-slot="{ active }">
              <button
                @click="$emit('logout')"
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
import { computed } from 'vue'
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
  ChevronUpDownIcon
} from '@heroicons/vue/24/outline'
import { RouterLink } from 'vue-router'

interface User {
  full_name?: string
  email?: string
}

interface NavigationItem {
  name: string
  to: string
  icon: any
}

interface Props {
  user?: User | null
  navigationItems?: NavigationItem[]
}

const props = withDefaults(defineProps<Props>(), {
  user: null,
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
}>()

const route = useRoute()

const isActiveRoute = (path: string) => {
  return route.path === path
}
</script> 