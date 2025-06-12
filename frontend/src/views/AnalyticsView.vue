<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold">Analytics</h1>
    <p class="mt-2 text-gray-600">View your analytics here.</p>

    <div v-if="isLoading" class="mt-8 text-center text-gray-500">Loading analytics...</div>
    <div v-else>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div class="bg-white rounded-lg shadow p-6 flex flex-col items-center">
          <span class="text-2xl font-bold">{{ events.length }}</span>
          <span class="text-gray-500">Total Events</span>
        </div>
        <div class="bg-white rounded-lg shadow p-6 flex flex-col items-center">
          <span class="text-2xl font-bold">{{ upcomingEvents.length }}</span>
          <span class="text-gray-500">Upcoming Events</span>
        </div>
        <div class="bg-white rounded-lg shadow p-6 flex flex-col items-center">
          <span class="text-2xl font-bold">{{ completedEvents.length }}</span>
          <span class="text-gray-500">Completed Events</span>
        </div>
      </div>

      <div class="mt-12 bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Events per Month</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full text-sm text-left">
            <thead>
              <tr>
                <th class="px-4 py-2">Month</th>
                <th class="px-4 py-2">Event Count</th>
                <th class="px-4 py-2">Bar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(count, month) in sortedEventsByMonth" :key="month">
                <td class="px-4 py-2 whitespace-nowrap">{{ month }}</td>
                <td class="px-4 py-2">{{ count }}</td>
                <td class="px-4 py-2">
                  <div class="bg-blue-100 h-4 rounded relative" style="min-width: 40px;">
                    <div
                      class="bg-blue-500 h-4 rounded"
                      :style="{ width: (count / maxEventsPerMonth * 100) + '%', minWidth: '4px' }"
                    ></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useEventStore } from '@/stores/events'

const eventStore = useEventStore()
const { events, isLoading, upcomingEvents, completedEvents } = storeToRefs(eventStore)
const { fetchEvents } = eventStore

onMounted(() => {
  if (!events.value.length) fetchEvents()
})

const eventsByMonth = computed(() => {
  // Group events by month (YYYY-MM)
  const map: Record<string, number> = {}
  events.value.forEach(e => {
    const date = new Date(e.occurrence)
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    map[key] = (map[key] || 0) + 1
  })
  return map
})

const sortedEventsByMonth = computed(() => {
  // Sort months ascending
  return Object.fromEntries(
    Object.entries(eventsByMonth.value).sort(([a], [b]) => a.localeCompare(b))
  )
})

const maxEventsPerMonth = computed(() => {
  const counts = Object.values(eventsByMonth.value)
  return counts.length ? Math.max(...counts) : 1
})
</script>
