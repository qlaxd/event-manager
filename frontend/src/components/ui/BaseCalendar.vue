<template>
  <div class="mb-8">
    <h3 class="text-lg font-medium text-gray-900 mb-4">{{ currentMonthYear }}</h3>
    <div class="bg-gray-50 rounded-lg p-4">
      <!-- Calendar Header -->
      <div class="flex items-center justify-between mb-4">
        <button 
          @click="previousMonth"
          class="p-1 hover:bg-gray-200 rounded"
        >
          <ChevronLeftIcon class="w-4 h-4" />
        </button>
        <h4 class="text-sm font-medium">{{ currentMonthYear }}</h4>
        <button 
          @click="nextMonth"
          class="p-1 hover:bg-gray-200 rounded"
        >
          <ChevronRightIcon class="w-4 h-4" />
        </button>
      </div>

      <!-- Calendar Grid -->
      <div class="grid grid-cols-7 gap-1 text-center text-xs">
        <!-- Week Headers -->
        <div class="p-2 text-gray-500 font-medium">S</div>
        <div class="p-2 text-gray-500 font-medium">M</div>
        <div class="p-2 text-gray-500 font-medium">T</div>
        <div class="p-2 text-gray-500 font-medium">W</div>
        <div class="p-2 text-gray-500 font-medium">T</div>
        <div class="p-2 text-gray-500 font-medium">F</div>
        <div class="p-2 text-gray-500 font-medium">S</div>

        <!-- Calendar Days -->
        <div v-for="(day, index) in calendarDays" :key="`${day.date}-${index}`" class="p-1">
          <button
            :class="[
              'w-8 h-8 rounded-full text-xs flex items-center justify-center transition-colors',
              day.isToday ? 'bg-gray-900 text-white' : 'hover:bg-gray-200',
              day.hasEvent ? 'relative' : '',
              !day.isCurrentMonth ? 'text-gray-300' : 'text-gray-900'
            ]"
            @click="selectDate(day)"
          >
            {{ day.day }}
            <span 
              v-if="day.hasEvent" 
              class="absolute top-0 right-0 w-2 h-2 bg-blue-500 rounded-full"
            ></span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'

interface CalendarDay {
  day: number
  date: string
  isCurrentMonth: boolean
  hasEvent: boolean
  isToday: boolean
}

interface Event {
  id: number
  occurrence: Date
}

// Props
const props = defineProps<{
  events?: Event[]
}>()

// Emits
const emit = defineEmits<{
  dateSelected: [date: string]
  monthChanged: [month: number, year: number]
}>()

// Reactive data
const currentDate = ref(new Date())
const today = ref(new Date())

// Computed properties
const currentMonthYear = computed(() => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    year: 'numeric'
  }).format(currentDate.value)
})

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  // Get first day of the month and last day of the month
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  
  // Get first day of the week for the first day of the month
  const firstDayOfWeek = firstDay.getDay()
  
  const days: CalendarDay[] = []
  
  // Add days from previous month
  const prevMonth = new Date(year, month - 1, 0)
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const day = prevMonth.getDate() - i
    const date = new Date(year, month - 1, day)
    const dateString = formatDateToString(date)
    days.push({
      day,
      date: dateString,
      isCurrentMonth: false,
      hasEvent: hasEventOnDate(date),
      isToday: isSameDay(date, today.value)
    })
  }
  
  // Add days from current month
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const date = new Date(year, month, day)
    const dateString = formatDateToString(date)
    days.push({
      day,
      date: dateString,
      isCurrentMonth: true,
      hasEvent: hasEventOnDate(date),
      isToday: isSameDay(date, today.value)
    })
  }
  
  // Add days from next month (only if needed to fill the grid)
  const totalCells = Math.ceil(days.length / 7) * 7
  const remainingDays = totalCells - days.length
  for (let day = 1; day <= remainingDays && days.length < 42; day++) {
    const date = new Date(year, month + 1, day)
    const dateString = formatDateToString(date)
    days.push({
      day,
      date: dateString,
      isCurrentMonth: false,
      hasEvent: hasEventOnDate(date),
      isToday: isSameDay(date, today.value)
    })
  }
  
  return days
})

// Methods
const formatDateToString = (date: Date): string => {
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  return `${year}-${month}-${day}`
}

const hasEventOnDate = (date: Date): boolean => {
  if (!props.events) return false
  
  return props.events.some(event => {
    const eventDate = new Date(event.occurrence)
    return isSameDay(eventDate, date)
  })
}

const isSameDay = (date1: Date, date2: Date): boolean => {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  )
}

const previousMonth = () => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(newDate.getMonth() - 1)
  currentDate.value = newDate
  
  emit('monthChanged', newDate.getMonth(), newDate.getFullYear())
}

const nextMonth = () => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(newDate.getMonth() + 1)
  currentDate.value = newDate
  
  emit('monthChanged', newDate.getMonth(), newDate.getFullYear())
}

const selectDate = (day: CalendarDay) => {
  emit('dateSelected', day.date)
}

// Watch for events changes to re-render calendar
watch(() => props.events, () => {
  // Force reactivity update
}, { deep: true })

onMounted(() => {
  // Update today's date every minute to keep the "today" highlight accurate
  setInterval(() => {
    today.value = new Date()
  }, 60000)
})
</script>

<style scoped>
/* Additional custom styles if needed */
.transition-colors {
  transition: background-color 0.2s ease;
}
</style>
