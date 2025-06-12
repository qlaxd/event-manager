<script setup lang="ts">
import { RouterView } from 'vue-router'
import ChatWidget from '@/components/ui/ChatWidget.vue'
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <RouterView/>
    <ChatWidget />
  </div>
</template>

<style scoped>
/* App-specific styles will go here */
</style>

 
