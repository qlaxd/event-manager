<script setup lang="ts">
import { RouterView } from 'vue-router'
import ChatWidget from '@/components/ui/ChatWidget.vue'
import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <RouterView/>
    <ChatWidget v-if="isAuthenticated" />
  </div>
</template>

<style scoped>
/* App-specific styles will go here */
</style>


