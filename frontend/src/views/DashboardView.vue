<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Mobile Header -->
    <header class="lg:hidden bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
      <div class="flex items-center justify-between px-4 py-3">
        <button
          @click="sidebarOpen = true"
          class="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
        >
          <Bars3Icon class="w-6 h-6" />
        </button>
        <div class="flex items-center">
          <div class="flex items-center justify-center w-8 h-8 bg-gray-900 text-white rounded-lg">
            <CalendarIcon class="w-5 h-5" />
          </div>
          <h1 class="ml-3 text-lg font-bold text-gray-900">EventManager</h1>
        </div>
        <button
          @click="showCreateEventModal = true"
          class="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
        >
          <PlusIcon class="w-6 h-6" />
        </button>
      </div>
    </header>

    <!-- Main Layout Container -->
    <div class="flex h-screen lg:h-screen">
      <!-- Left Sidebar -->
      <Sidebar 
        :user="currentUser" 
        :is-open="sidebarOpen"
        @logout="handleLogout"
        @close="sidebarOpen = false"
      />

      <!-- Main Content -->
      <main class="flex-1 flex flex-col lg:flex-row w-full">
        <!-- Dashboard Content -->
        <div class="flex-1 p-4 sm:p-6 overflow-y-auto">
          <!-- Header -->
          <div class="mb-6">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
                <p class="text-gray-600">Welcome back! Here's what's happening with your events.</p>
              </div>
              <Button 
                variant="primary" 
                @click="showCreateEventModal = true"
                class="hidden lg:flex"
              >
                <PlusIcon class="w-4 h-4 mr-2" />
                Create Event
              </Button>
            </div>
          </div>

          <!-- Stats Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
            <div class="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
              <div class="flex items-center">
                <div class="p-2 bg-blue-100 rounded-lg">
                  <CalendarDaysIcon class="w-6 h-6 text-blue-600" />
                </div>
                <div class="ml-4">
                  <p class="text-xl sm:text-2xl font-bold text-gray-900">24</p>
                  <p class="text-sm text-gray-500">Total Events</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
              <div class="flex items-center">
                <div class="p-2 bg-yellow-100 rounded-lg">
                  <ClockIcon class="w-6 h-6 text-yellow-600" />
                </div>
                <div class="ml-4">
                  <p class="text-xl sm:text-2xl font-bold text-gray-900">8</p>
                  <p class="text-sm text-gray-500">Upcoming</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
              <div class="flex items-center">
                <div class="p-2 bg-green-100 rounded-lg">
                  <CheckCircleIcon class="w-6 h-6 text-green-600" />
                </div>
                <div class="ml-4">
                  <p class="text-xl sm:text-2xl font-bold text-gray-900">16</p>
                  <p class="text-sm text-gray-500">Completed</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-gray-200">
              <div class="flex items-center">
                <div class="p-2 bg-purple-100 rounded-lg">
                  <CalendarIcon class="w-6 h-6 text-purple-600" />
                </div>
                <div class="ml-4">
                  <p class="text-xl sm:text-2xl font-bold text-gray-900">5</p>
                  <p class="text-sm text-gray-500">This Week</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Events Section -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="px-4 sm:px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-medium text-gray-900">Upcoming Events</h2>
                <button class="text-sm text-blue-600 hover:text-blue-800">View All</button>
              </div>
            </div>

            <div class="p-4 sm:p-6">
              <!-- Search and Filter Bar -->
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                <div class="flex-1 max-w-full sm:max-w-lg">
                  <Input
                    v-model="searchQuery"
                    placeholder="Search events..."
                    class="w-full"
                  >
                    <template #icon-left>
                      <MagnifyingGlassIcon class="w-4 h-4 text-gray-400" />
                    </template>
                  </Input>
                </div>
                <div class="flex items-center space-x-3">
                  <Dropdown>
                    <template #trigger>
                      <Button variant="outline" size="sm" class="flex-shrink-0">
                        <FunnelIcon class="w-4 h-4 mr-2" />
                        <span class="hidden sm:inline">Filter</span>
                      </Button>
                    </template>
                    <DropdownItem>All Events</DropdownItem>
                    <DropdownItem>Upcoming</DropdownItem>
                    <DropdownItem>Completed</DropdownItem>
                    <DropdownItem>This Week</DropdownItem>
                  </Dropdown>
                </div>
              </div>

              <!-- Events List -->
              <div class="space-y-4">
                <div
                  v-for="event in filteredEvents"
                  :key="event.id"
                  class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 gap-4"
                >
                  <div class="flex items-center flex-1 min-w-0">
                    <div class="flex items-center justify-center w-10 h-10 rounded-lg mr-4 flex-shrink-0"
                         :class="getEventIconBg(event.type)">
                      <component :is="getEventIcon(event.type)" class="w-5 h-5" :class="getEventIconColor(event.type)" />
                    </div>
                    <div class="min-w-0 flex-1">
                      <h3 class="text-sm font-medium text-gray-900 truncate">{{ event.title }}</h3>
                      <p class="text-sm text-gray-500 truncate">{{ event.description }}</p>
                      <p class="text-xs text-gray-400 mt-1">{{ formatDate(event.occurrence) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center justify-between sm:justify-end space-x-2 flex-shrink-0">
                    <span
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getStatusBadge(event.status)"
                    >
                      {{ event.status }}
                    </span>
                    <Menu as="div" class="relative">
                      <MenuButton class="flex items-center justify-center w-8 h-8 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100">
                        <EllipsisVerticalIcon class="w-4 h-4" />
                      </MenuButton>
                      <transition
                        enter-active-class="transition duration-100 ease-out"
                        enter-from-class="transform scale-95 opacity-0"
                        enter-to-class="transform scale-100 opacity-100"
                        leave-active-class="transition duration-75 ease-in"
                        leave-from-class="transform scale-100 opacity-100"
                        leave-to-class="transform scale-95 opacity-0"
                      >
                        <MenuItems class="absolute right-0 z-10 w-48 mt-1 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                          <MenuItem v-slot="{ active }">
                            <button
                              :class="[
                                active ? 'bg-gray-100' : '',
                                'flex items-center w-full px-3 py-2 text-sm text-gray-700'
                              ]"
                              @click="editEvent(event)"
                            >
                              <PencilIcon class="w-4 h-4 mr-2" />
                              Edit
                            </button>
                          </MenuItem>
                          <MenuItem v-slot="{ active }">
                            <button
                              :class="[
                                active ? 'bg-gray-100' : '',
                                'flex items-center w-full px-3 py-2 text-sm text-red-700'
                              ]"
                              @click="deleteEvent(event)"
                            >
                              <TrashIcon class="w-4 h-4 mr-2" />
                              Delete
                            </button>
                          </MenuItem>
                        </MenuItems>
                      </transition>
                    </Menu>
                  </div>
                </div>
              </div>

              <!-- Empty State -->
              <div v-if="filteredEvents.length === 0" class="text-center py-12">
                <CalendarDaysIcon class="mx-auto h-12 w-12 text-gray-400" />
                <h3 class="mt-2 text-sm font-medium text-gray-900">No events found</h3>
                <p class="mt-1 text-sm text-gray-500">Get started by creating your first event.</p>
                <div class="mt-6">
                  <Button variant="primary" @click="showCreateEventModal = true">
                    <PlusIcon class="w-4 h-4 mr-2" />
                    Create Event
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Sidebar -->
        <aside class="hidden xl:block w-80 bg-white shadow-lg p-6 overflow-y-auto">
          <!-- Quick Actions -->
          <div class="mb-8">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div class="space-y-3">
              <Button variant="primary" full-width @click="showCreateEventModal = true">
                <PlusIcon class="w-4 h-4 mr-2" />
                Create Event
              </Button>
              <Button variant="outline" full-width>
                <CalendarIcon class="w-4 h-4 mr-2" />
                View Calendar
              </Button>
              <Button variant="outline" full-width>
                <ArrowDownTrayIcon class="w-4 h-4 mr-2" />
                Export Events
              </Button>
            </div>
          </div>

          <!-- Calendar Widget -->
          <Calendar 
            :events="events" 
            @dateSelected="handleDateSelected"
            @monthChanged="handleMonthChanged"
          />

          <!-- Help Desk -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Help Desk</h3>
            <div class="bg-blue-50 rounded-lg p-4">
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <ChatBubbleLeftRightIcon class="w-6 h-6 text-blue-600" />
                </div>
                <div class="ml-3">
                  <h4 class="text-sm font-medium text-blue-900">AI Assistant</h4>
                  <p class="text-sm text-blue-700 mb-3">Ask me anything about managing your events!</p>
                  <Input
                    v-model="helpQuery"
                    placeholder="Type your question..."
                    size="sm"
                    class="mb-3"
                  />
                  <div class="flex flex-col sm:flex-row gap-2">
                    <Button variant="primary" size="xs" class="flex-1">
                      Send
                    </Button>
                    <Button variant="outline" size="xs" class="flex-1">
                      <PhoneIcon class="w-3 h-3 mr-1" />
                      <span class="hidden sm:inline">Call Support</span>
                      <span class="sm:hidden">Call</span>
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </main>
    </div>

    <!-- Create Event Modal -->
    <Modal :show="showCreateEventModal" @close="showCreateEventModal = false" title="Create New Event">
      <div class="space-y-4">
        <Input
          v-model="newEvent.title"
          label="Event Title"
          placeholder="Enter event title"
          required
        />
        <Input
          v-model="newEvent.occurrence"
          label="Date & Time"
          type="datetime-local"
          required
        />
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            v-model="newEvent.description"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter event description (optional)"
          ></textarea>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end space-x-3">
          <Button variant="outline" @click="showCreateEventModal = false">
            Cancel
          </Button>
          <Button variant="primary" @click="createEvent">
            Create Event
          </Button>
        </div>
      </template>
    </Modal>

    <!-- Mobile Quick Actions FAB -->
    <div class="xl:hidden fixed bottom-6 right-6 z-40">
      <div class="relative">
        <button
          @click="showQuickActions = !showQuickActions"
          :class="[
            'w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg',
            'flex items-center justify-center transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
          ]"
        >
          <PlusIcon v-if="!showQuickActions" class="w-6 h-6" />
          <XMarkIcon v-else class="w-6 h-6" />
        </button>
        
        <!-- Quick Actions Menu -->
        <transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="transform scale-95 opacity-0"
          enter-to-class="transform scale-100 opacity-100"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="transform scale-100 opacity-100"
          leave-to-class="transform scale-95 opacity-0"
        >
          <div
            v-if="showQuickActions"
            class="absolute bottom-16 right-0 w-48 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 py-2"
          >
            <button
              @click="handleCreateEvent"
              class="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-gray-100"
            >
              <PlusIcon class="w-4 h-4 mr-3 text-gray-400" />
              Create Event
            </button>
            <button
              class="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-gray-100"
            >
              <CalendarIcon class="w-4 h-4 mr-3 text-gray-400" />
              View Calendar
            </button>
            <button
              class="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-gray-100"
            >
              <ArrowDownTrayIcon class="w-4 h-4 mr-3 text-gray-400" />
              Export Events
            </button>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'
import {
  CalendarIcon,
  ClockIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EllipsisVerticalIcon,
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  ChatBubbleLeftRightIcon,
  PhoneIcon,
  UsersIcon,
  PresentationChartBarIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  PlusIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'

import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Modal from '@/components/ui/Modal.vue'
import Dropdown from '@/components/ui/Dropdown.vue'
import DropdownItem from '@/components/ui/DropdownItem.vue'
import Calendar from '@/components/ui/Calendar.vue'
import { Sidebar } from '@/components/ui'
import { RouterLink } from 'vue-router'

const router = useRouter()

// Reactive data
const searchQuery = ref('')
const helpQuery = ref('')
const sidebarOpen = ref(false)
const showQuickActions = ref(false)

// Current user data (could come from a store like useAuthStore)
const currentUser = ref({
  full_name: 'John Doe',
  email: 'john@example.com'
})
const showCreateEventModal = ref(false)
const newEvent = ref({
  title: '',
  occurrence: '',
  description: ''
})

// Sample events data
const events = ref([
  {
    id: 1,
    title: 'Team Meeting',
    description: 'Weekly team sync and project updates',
    occurrence: new Date('2025-01-15T14:00:00'),
    status: 'Upcoming',
    type: 'meeting'
  },
  {
    id: 2,
    title: 'Product Launch',
    description: 'Official launch event for the new product line',
    occurrence: new Date('2025-01-20T14:00:00'),
    status: 'Upcoming',
    type: 'launch'
  },
  {
    id: 3,
    title: 'Client Presentation',
    description: 'Quarterly review with key stakeholders',
    occurrence: new Date('2025-01-12T15:30:00'),
    status: 'Completed',
    type: 'presentation'
  }
])

// Computed properties
const filteredEvents = computed(() => {
  if (!searchQuery.value) return events.value
  return events.value.filter(event =>
    event.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    event.description.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

// Methods
const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const getEventIcon = (type: string) => {
  const icons: Record<string, any> = {
    meeting: UsersIcon,
    launch: PresentationChartBarIcon,
    presentation: ChartBarIcon
  }
  return icons[type] || CalendarIcon
}

const getEventIconBg = (type: string) => {
  const colors: Record<string, string> = {
    meeting: 'bg-blue-100',
    launch: 'bg-green-100',
    presentation: 'bg-purple-100'
  }
  return colors[type] || 'bg-gray-100'
}

const getEventIconColor = (type: string) => {
  const colors: Record<string, string> = {
    meeting: 'text-blue-600',
    launch: 'text-green-600',
    presentation: 'text-purple-600'
  }
  return colors[type] || 'text-gray-600'
}

const getStatusBadge = (status: string) => {
  const badges: Record<string, string> = {
    'Upcoming': 'bg-yellow-100 text-yellow-800',
    'Completed': 'bg-green-100 text-green-800',
    'Cancelled': 'bg-red-100 text-red-800'
  }
  return badges[status] || 'bg-gray-100 text-gray-800'
}

const createEvent = () => {
  if (newEvent.value.title && newEvent.value.occurrence) {
    events.value.push({
      id: events.value.length + 1,
      title: newEvent.value.title,
      description: newEvent.value.description,
      occurrence: new Date(newEvent.value.occurrence),
      status: 'Upcoming',
      type: 'meeting'
    })
    
    // Reset form
    newEvent.value = { title: '', occurrence: '', description: '' }
    showCreateEventModal.value = false
  }
}

const handleCreateEvent = () => {
  showCreateEventModal.value = true
  showQuickActions.value = false
}

const editEvent = (event: any) => {
  console.log('Edit event:', event)
  // Implementation for edit functionality
}

const deleteEvent = (event: any) => {
  const index = events.value.findIndex(e => e.id === event.id)
  if (index > -1) {
    events.value.splice(index, 1)
  }
}

const handleDateSelected = (date: string) => {
  console.log('Selected date:', date)
  // You can add logic here to handle date selection
  // For example, filter events by date, show date details, etc.
}

const handleMonthChanged = (month: number, year: number) => {
  console.log('Month changed:', month, year)
  // You can add logic here to handle month changes
  // For example, load events for the new month, update analytics, etc.
}

const handleLogout = () => {
  console.log('Logout clicked')
  // Add logout logic here
  // For example: authStore.logout() then router.push('/login')
  router.push('/login')
}

onMounted(() => {
  // Initialize component
  
  // Close quick actions when clicking outside
  const handleClickOutside = (event: Event) => {
    const target = event.target as Element
    if (!target.closest('.fixed.bottom-6.right-6')) {
      showQuickActions.value = false
    }
  }
  
  document.addEventListener('click', handleClickOutside)
  
  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
  })
})
</script>

<style scoped>
/* Custom styles if needed */
</style>