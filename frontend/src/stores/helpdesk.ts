import { defineStore } from 'pinia'
import { ref } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { ChatMessage } from '@/types'
import helpdeskService from '@/services/helpdesk'

export const useHelpdeskStore = defineStore('helpdesk', () => {
  // State
  const messages = ref<ChatMessage[]>([])
  const sessionId = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isTranscribing = ref(false)
  const transcriptionError = ref<string | null>(null)

  // Actions
  function startSession() {
    sessionId.value = uuidv4()
    messages.value = [{
      id: uuidv4(),
      sender: 'bot',
      message: "Hello! I'm the event assistant. How can I help you today?",
      timestamp: new Date().toISOString()
    }]
  }

  async function sendMessage(messageText: string) {
    if (!sessionId.value) {
      startSession()
    }

    const userMessage: ChatMessage = {
      id: uuidv4(),
      sender: 'user',
      message: messageText,
      timestamp: new Date().toISOString()
    }
    messages.value.push(userMessage)
    isLoading.value = true
    error.value = null

    try {
      const response = await helpdeskService.sendMessage({
        message: messageText,
        session_id: sessionId.value!
      })
      const botMessage: ChatMessage = {
        id: uuidv4(),
        sender: 'bot',
        message: response.response,
        timestamp: new Date().toISOString(),
        quick_replies: response.quick_replies
      }
      messages.value.push(botMessage)

    } catch (err: unknown) {
      error.value = 'The chatbot is currently unavailable. Please try again later.'
      console.error('Failed to send message:', err)
      const errorMessage: ChatMessage = {
        id: uuidv4(),
        sender: 'bot',
        message: 'Sorry, I am having trouble connecting. Please try again later.',
        timestamp: new Date().toISOString()
      }
      messages.value.push(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  async function transcribeAudio(audioBlob: Blob): Promise<string> {
    isTranscribing.value = true
    transcriptionError.value = null
    try {
      const response = await helpdeskService.transcribeAudio(audioBlob)
      return response.text
    } catch (err) {
      transcriptionError.value = 'Failed to transcribe audio. Please try again.'
      console.error('Transcription error:', err)
      throw new Error(transcriptionError.value)
    } finally {
      isTranscribing.value = false
    }
  }

  return {
    messages,
    sessionId,
    isLoading,
    error,
    isTranscribing,
    transcriptionError,
    startSession,
    sendMessage,
    transcribeAudio,
  }
}) 