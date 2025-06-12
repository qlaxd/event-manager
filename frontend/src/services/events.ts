import apiClient from './api'
import type { Event, EventCreate, EventUpdate } from '@/types'

interface PaginatedEventsResponse {
  data: Event[]
  total: number
  limit: number
  offset: number
}

class EventService {
  async getEvents(params: Record<string, string | number | boolean> = {}): Promise<PaginatedEventsResponse> {
    const response = await apiClient.get<PaginatedEventsResponse>('/events', { params })
    return response.data
  }

  async getEvent(id: string): Promise<Event> {
    const response = await apiClient.get<Event>(`/events/${id}`)
    return response.data
  }

  async createEvent(data: EventCreate): Promise<Event> {
    const response = await apiClient.post<Event>('/events', data)
    return response.data
  }

  async updateEvent(id: string, data: EventUpdate): Promise<Event> {
    const response = await apiClient.patch<Event>(`/events/${id}`, data)
    return response.data
  }

  async deleteEvent(id: string): Promise<void> {
    await apiClient.delete(`/events/${id}`)
  }
}

export default new EventService() 