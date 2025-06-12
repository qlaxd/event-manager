import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Event, EventCreate, EventUpdate } from '@/types'
import eventService from '@/services/events'

export const useEventStore = defineStore('events', () => {
  // State
  const events = ref<Event[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const upcomingEvents = computed(() => 
    events.value
      .filter(e => new Date(e.occurrence) > new Date())
      .sort((a, b) => new Date(a.occurrence).getTime() - new Date(b.occurrence).getTime())
  )

  const completedEvents = computed(() =>
    events.value.filter(e => new Date(e.occurrence) <= new Date())
  )

  // Actions
  async function fetchEvents() {
    isLoading.value = true
    error.value = null
    try {
      const response = await eventService.getEvents()
      events.value = response.data
    } catch (err: unknown) {
      error.value = 'Failed to fetch events.'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function createEvent(eventData: EventCreate) {
    isLoading.value = true
    error.value = null
    try {
      const newEvent = await eventService.createEvent(eventData)
      events.value.push(newEvent)
    } catch (err: unknown) {
      error.value = 'Failed to create event.'
      console.error(err)
      throw err // Re-throw to be handled in the component
    } finally {
      isLoading.value = false
    }
  }

  async function updateEvent(eventId: string, eventData: EventUpdate) {
    isLoading.value = true
    error.value = null
    try {
      const updatedEvent = await eventService.updateEvent(eventId, eventData)
      const index = events.value.findIndex(e => e.id === eventId)
      if (index !== -1) {
        events.value[index] = updatedEvent
      }
    } catch (err: unknown) {
      error.value = 'Failed to update event.'
      console.error(err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteEvent(eventId: string) {
    isLoading.value = true
    error.value = null
    try {
      await eventService.deleteEvent(eventId)
      events.value = events.value.filter(e => e.id !== eventId)
    } catch (err: unknown) {
      error.value = 'Failed to delete event.'
      console.error(err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    events,
    isLoading,
    error,
    upcomingEvents,
    completedEvents,
    fetchEvents,
    createEvent,
    updateEvent,
    deleteEvent,
  }
}) 