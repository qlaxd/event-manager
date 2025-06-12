<template>
  <div>
    <button
      class="fixed bottom-6 right-6 z-50 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg w-14 h-14 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-blue-400"
      @click="toggleChat"
      aria-label="Open helpdesk chat"
    >
      <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.77 9.77 0 01-4-.8L3 20l.8-4A8.96 8.96 0 013 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    </button>
    <transition name="fade">
      <div
        v-if="open"
        class="fixed bottom-24 right-6 z-50 w-80 max-w-full bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col h-[500px]"
      >
        <ChatView @close="toggleChat" />
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ChatView from '@/views/ChatView.vue'

const open = ref(false)
const toggleChat = () => {
  open.value = !open.value
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
