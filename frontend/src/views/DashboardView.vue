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
          @click="openCreateModal"
          class="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
        >
          <PlusIcon class="w-6 h-6" />
        </button>
      </div>
    </header>

    <!-- Main Layout Container -->
    <div class="flex h-screen">
      <TheSidebar 
        :user="user" 
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
                <p class="text-gray-600">Welcome back, {{ user?.full_name }}!</p>
              </div>
              <BaseButton 
                variant="primary" 
                @click="openCreateModal"
                class="hidden lg:flex"
              >
                <PlusIcon class="w-4 h-4 mr-2" />
                Create Event
              </BaseButton>
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
                  <p class="text-xl sm:text-2xl font-bold text-gray-900">{{ events.length }}</p>
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
                  <p class="text-xl sm:text-2xl font-bold text-gray-900">{{ upcomingEvents.length }}</p>
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
                  <p class="text-xl sm:text-2xl font-bold text-gray-900">{{ completedEvents.length }}</p>
                  <p class="text-sm text-gray-500">Completed</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Events Section -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="px-4 sm:px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">Events</h2>
            </div>

            <div class="p-4 sm:p-6">
              <!-- Search and Filter Bar -->
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                <div class="flex-1 max-w-full sm:max-w-lg">
                  <BaseInput
                    v-model="searchQuery"
                    placeholder="Search events..."
                    class="w-full"
                  >
                    <template #icon-left>
                      <MagnifyingGlassIcon class="w-4 h-4 text-gray-400" />
                    </template>
                  </BaseInput>
                </div>
              </div>

              <!-- Events List -->
              <div v-if="isLoading" class="text-center py-12">Loading events...</div>
              <div v-else-if="error" class="text-center py-12 text-red-500">{{ error }}</div>
              <div v-else-if="filteredEvents.length === 0" class="text-center py-12">
                <CalendarDaysIcon class="mx-auto h-12 w-12 text-gray-400" />
                <h3 class="mt-2 text-sm font-medium text-gray-900">No events found</h3>
                <p class="mt-1 text-sm text-gray-500">Get started by creating your first event.</p>
                <div class="mt-6">
                  <BaseButton variant="primary" @click="openCreateModal">
                    <PlusIcon class="w-4 h-4 mr-2" />
                    Create Event
                  </BaseButton>
                </div>
              </div>
              <div v-else class="space-y-4">
                <div
                  v-for="event in filteredEvents"
                  :key="event.id"
                  class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 border rounded-lg hover:bg-gray-50 gap-4"
                >
                  <div class="flex items-center flex-1 min-w-0">
                    <div class="flex-shrink-0 mr-4">
                      <CalendarIcon class="w-10 h-10 text-gray-400" />
                    </div>
                    <div class="min-w-0 flex-1">
                      <h3 class="text-sm font-medium text-gray-900 truncate">{{ event.title }}</h3>
                      <p class="text-sm text-gray-500 truncate">{{ event.description }}</p>
                      <p class="text-xs text-gray-400 mt-1">{{ formatDate(event.occurrence) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2 flex-shrink-0">
                    <BaseButton size="sm" variant="outline" @click="openEditModal(event)">Edit</BaseButton>
                    <BaseButton size="sm" variant="danger" @click="handleDeleteEvent(event.id)">Delete</BaseButton>
                  </div>
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
              <BaseButton variant="primary" full-width @click="openCreateModal">
                <PlusIcon class="w-4 h-4 mr-2" />
                Create Event
              </BaseButton>
              <BaseButton variant="outline" full-width @click="goToChat">
                <ChatBubbleLeftRightIcon class="w-4 h-4 mr-2" />
                Helpdesk
              </BaseButton>
            </div>
          </div>
        </aside>
      </main>
    </div>

    <!-- Create/Edit Event Modal -->
    <BaseModal :show="showEventModal" @close="closeEventModal" :title="isEditMode ? 'Edit Event' : 'Create New Event'">
      <form @submit.prevent="handleSaveEvent" class="space-y-4">
        <BaseInput v-model="eventForm.title" label="Event Title" required />
        <BaseInput v-model="eventForm.occurrence" label="Date & Time" type="datetime-local" required />
        <textarea v-model="eventForm.description" placeholder="Description" rows="4" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"></textarea>
      </form>
      <template #footer>
        <div class="flex justify-end space-x-3">
          <BaseButton variant="outline" @click="closeEventModal">Cancel</BaseButton>
          <BaseButton variant="primary" @click="handleSaveEvent" :loading="isLoading">
            {{ isEditMode ? 'Save Changes' : 'Create Event' }}
          </BaseButton>
        </div>
      </template>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import {
  CalendarIcon,
  ClockIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon,
  ChatBubbleLeftRightIcon,
  CalendarDaysIcon,
  PlusIcon,
  Bars3Icon,
} from '@heroicons/vue/24/outline'

import {
  BaseButton,
  BaseInput,
  BaseModal,
  TheSidebar,
} from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { useEventStore } from '@/stores/events'
import type { Event as EventType, EventCreate } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const eventStore = useEventStore()
const { events, isLoading, error, upcomingEvents, completedEvents } = storeToRefs(eventStore)
const { fetchEvents, createEvent, updateEvent, deleteEvent: deleteEventFromStore } = eventStore

const user = computed(() => authStore.user)
const sidebarOpen = ref(false)
const searchQuery = ref('')

const filteredEvents = computed(() => {
  if (!events.value) return []
  if (!searchQuery.value) return events.value
  return events.value.filter(event =>
    event.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const showEventModal = ref(false)
const isEditMode = ref(false)
const eventForm = reactive<EventCreate & { id?: string }>({
  title: '',
  description: '',
  occurrence: ''
})

onMounted(() => {
  fetchEvents()
})

const formatDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }
  return new Date(dateString).toLocaleDateString(undefined, options)
}

const openCreateModal = () => {
  isEditMode.value = false
  Object.assign(eventForm, { id: undefined, title: '', description: '', occurrence: '' })
  showEventModal.value = true
}

const openEditModal = (event: EventType) => {
  isEditMode.value = true
  Object.assign(eventForm, {
    id: event.id,
    title: event.title,
    description: event.description,
    occurrence: event.occurrence.substring(0, 16) // Format for datetime-local input
  })
  showEventModal.value = true
}

const closeEventModal = () => {
  showEventModal.value = false
}

const handleSaveEvent = async () => {
  const eventData = {
    title: eventForm.title,
    description: eventForm.description,
    occurrence: new Date(eventForm.occurrence).toISOString()
  }

  if (isEditMode.value) {
    if (eventForm.id) {
      await updateEvent(eventForm.id, eventData)
    }
  } else {
    await createEvent(eventData)
  }
  closeEventModal()
}

const handleDeleteEvent = async (eventId: string) => {
  if (confirm('Are you sure you want to delete this event?')) {
    await deleteEventFromStore(eventId)
  }
}

const goToChat = () => {
  router.push('/chat')
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}
</script>

<style scoped>
/* Custom styles if needed */
</style>