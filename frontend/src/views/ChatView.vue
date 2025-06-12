<template>
  <div class="flex flex-col h-full bg-gray-100 rounded-lg">
    <!-- Header -->
    <header class="flex items-center justify-between bg-white shadow-sm border-b border-gray-200 p-4 rounded-t-lg">
      <h1 class="text-xl font-bold text-gray-900">Helpdesk Chat</h1>
       <button @click="$emit('close')" class="p-1 rounded-full text-gray-400 hover:bg-gray-200 hover:text-gray-600 focus:outline-none">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </header>

    <!-- Chat Messages -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
      <div v-for="message in helpdeskStore.messages" :key="message.id"
           :class="['flex', message.sender === 'user' ? 'justify-end' : 'justify-start']">
        <div :class="[
            'max-w-lg px-4 py-2 rounded-lg shadow',
            message.sender === 'user'
              ? 'bg-blue-500 text-white'
              : 'bg-white text-gray-800'
          ]">
          <p>{{ message.message }}</p>
          <div class="text-xs mt-1" :class="message.sender === 'user' ? 'text-blue-100' : 'text-gray-400'">
            {{ new Date(message.timestamp).toLocaleTimeString() }}
          </div>
        </div>
      </div>
       <div v-if="helpdeskStore.isLoading" class="flex justify-start">
          <div class="bg-white text-gray-800 px-4 py-2 rounded-lg shadow">
              Typing...
          </div>
       </div>
    </div>

    <!-- Message Input -->
    <footer class="bg-white border-t border-gray-200 p-4 rounded-b-lg">
      <div v-if="transcriptionError" class="text-red-500 text-xs mb-2">{{ transcriptionError }}</div>
      <div class="flex items-center space-x-3">
        <VoiceRecorder
          @transcription-complete="onTranscriptionComplete"
          @error="handleTranscriptionError"
        />
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="Type your message..."
          class="flex-1 w-full px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500"
          :disabled="helpdeskStore.isLoading || helpdeskStore.isTranscribing"
        />
        <button
          @click="sendMessage"
          :disabled="!newMessage || helpdeskStore.isLoading || helpdeskStore.isTranscribing"
          class="px-6 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:bg-blue-300"
        >
          Send
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useHelpdeskStore } from '@/stores/helpdesk'
import VoiceRecorder from '@/components/chat/VoiceRecorder.vue'

defineEmits(['close'])

const helpdeskStore = useHelpdeskStore()
const newMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const transcriptionError = ref<string | null>(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

onMounted(() => {
  if (!helpdeskStore.sessionId) {
    helpdeskStore.startSession()
  }
  scrollToBottom()
})

watch(() => helpdeskStore.messages, () => {
  scrollToBottom()
}, { deep: true })

const sendMessage = () => {
  if (newMessage.value.trim()) {
    helpdeskStore.sendMessage(newMessage.value.trim())
    newMessage.value = ''
  }
}

const onTranscriptionComplete = (transcription: string) => {
  newMessage.value = transcription
}

const handleTranscriptionError = (errorMessage: string) => {
  transcriptionError.value = errorMessage
  console.error(errorMessage)
  setTimeout(() => transcriptionError.value = null, 3000)
}
</script>
