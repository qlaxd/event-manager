<template>
  <div class="flex flex-col h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200 p-4">
      <h1 class="text-xl font-bold text-gray-900">Helpdesk Chat</h1>
    </header>

    <!-- Chat Messages -->
    <div class="flex-1 overflow-y-auto p-6 space-y-4">
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
    <footer class="bg-white border-t border-gray-200 p-4">
      <div class="flex items-center space-x-3">
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="Type your message..."
          class="flex-1 w-full px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500"
          :disabled="helpdeskStore.isLoading"
        />
        <button
          @click="sendMessage"
          :disabled="!newMessage || helpdeskStore.isLoading"
          class="px-6 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:bg-blue-300"
        >
          Send
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useHelpdeskStore } from '@/stores/helpdesk'

const helpdeskStore = useHelpdeskStore()
const newMessage = ref('')

onMounted(() => {
  if (!helpdeskStore.sessionId) {
    helpdeskStore.startSession()
  }
})

const sendMessage = () => {
  if (newMessage.value.trim()) {
    helpdeskStore.sendMessage(newMessage.value.trim())
    newMessage.value = ''
  }
}
</script>
