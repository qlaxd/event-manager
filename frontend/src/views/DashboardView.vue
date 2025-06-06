<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Main Layout Container -->
    <div class="flex h-screen">
      <!-- Left Sidebar -->
      <Sidebar 
        :user="currentUser" 
        @logout="handleLogout" 
      />

      <!-- Main Content -->
      <main class="flex-1 flex">
        <!-- Dashboard Content -->
        <div class="flex-1 p-6 overflow-y-auto">
          <!-- Header -->
          <div class="mb-6">
            <div class="flex items-center justify-between">
              <div>
                <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
                <p class="text-gray-600">Welcome back! Here's what's happening with your events.</p>
              </div>
              <Button variant="primary" @click="showCreateEventModal = true">
                <PlusIcon class="w-4 h-4 mr-2" />
                Create Event
              </Button>
            </div>
          </div>

          <!-- Stats Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div class="flex items-center">
                <div class="p-2 bg-blue-100 rounded-lg">
                  <CalendarDaysIcon class="w-6 h-6 text-blue-600" />
                </div>
                <div class="ml-4">
                  <p class="text-2xl font-bold text-gray-900">24</p>
                  <p class="text-sm text-gray-500">Total Events</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div class="flex items-center">
                <div class="p-2 bg-yellow-100 rounded-lg">
                  <ClockIcon class="w-6 h-6 text-yellow-600" />
                </div>
                <div class="ml-4">
                  <p class="text-2xl font-bold text-gray-900">8</p>
                  <p class="text-sm text-gray-500">Upcoming</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div class="flex items-center">
                <div class="p-2 bg-green-100 rounded-lg">
                  <CheckCircleIcon class="w-6 h-6 text-green-600" />
                </div>
                <div class="ml-4">
                  <p class="text-2xl font-bold text-gray-900">16</p>
                  <p class="text-sm text-gray-500">Completed</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div class="flex items-center">
                <div class="p-2 bg-purple-100 rounded-lg">
                  <CalendarIcon class="w-6 h-6 text-purple-600" />
                </div>
                <div class="ml-4">
                  <p class="text-2xl font-bold text-gray-900">5</p>
                  <p class="text-sm text-gray-500">This Week</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Events Section -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-medium text-gray-900">Upcoming Events</h2>
                <button class="text-sm text-blue-600 hover:text-blue-800">View All</button>
              </div>
            </div>

            <div class="p-6">
              <!-- Search and Filter Bar -->
              <div class="flex items-center justify-between mb-6">
                <div class="flex-1 max-w-lg">
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
                <div class="flex items-center space-x-3 ml-4">
                  <Dropdown>
                    <template #trigger>
                      <Button variant="outline" size="sm">
                        <FunnelIcon class="w-4 h-4 mr-2" />
                        Filter
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
                  class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div class="flex items-center">
                    <div class="flex items-center justify-center w-10 h-10 rounded-lg mr-4"
                         :class="getEventIconBg(event.type)">
                      <component :is="getEventIcon(event.type)" class="w-5 h-5" :class="getEventIconColor(event.type)" />
                    </div>
                    <div>
                      <h3 class="text-sm font-medium text-gray-900">{{ event.title }}</h3>
                      <p class="text-sm text-gray-500">{{ event.description }}</p>
                      <p class="text-xs text-gray-400 mt-1">{{ formatDate(event.occurrence) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
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
        <aside class="w-80 bg-white shadow-lg p-6 overflow-y-auto">
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
                  <div class="flex space-x-2">
                    <Button variant="primary" size="xs">
                      Send
                    </Button>
                    <Button variant="outline" size="xs">
                      <PhoneIcon class="w-3 h-3 mr-1" />
                      Call Support
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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
  ChartBarIcon
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
})
</script>

<style scoped>
/* Custom styles if needed */
</style>