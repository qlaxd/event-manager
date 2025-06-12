<template>
  <div>
    <button
      @click="toggleRecording"
      :disabled="status === 'requesting_permission' || status === 'transcribing'"
      :class="[
        'p-2 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
        buttonClasses,
      ]"
      aria-label="Record voice message"
    >
      <div v-if="status === 'recording'" class="w-5 h-5 flex items-center justify-center">
        <span class="w-2.5 h-2.5 bg-white rounded-full"></span>
      </div>
      <svg
        v-else-if="status === 'transcribing'"
        class="animate-spin h-5 w-5 text-white"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      <svg
        v-else
        class="w-5 h-5"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          fill-rule="evenodd"
          d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8h-1a6 6 0 11-12 0H3a7.001 7.001 0 006 6.93V17H7a1 1 0 100 2h6a1 1 0 100-2h-2v-2.07z"
          clip-rule="evenodd"
        />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAudioRecorder } from '@/composables/useAudioRecorder'
import { useHelpdeskStore } from '@/stores/helpdesk'

type RecorderStatus = 'idle' | 'requesting_permission' | 'recording' | 'transcribing' | 'error'

const emit = defineEmits<{
  'transcription-complete': [text: string]
  'error': [message: string]
}>()

const helpdeskStore = useHelpdeskStore()
const { isRecording, startRecording, stopRecording } = useAudioRecorder()
const status = ref<RecorderStatus>('idle')

const buttonClasses = computed(() => {
  switch (status.value) {
    case 'recording':
      return 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-500'
    case 'transcribing':
      return 'bg-blue-500 text-white cursor-not-allowed'
    case 'error':
      return 'bg-yellow-400 text-white hover:bg-yellow-500 focus:ring-yellow-400'
    default:
      return 'text-gray-500 hover:text-blue-600 hover:bg-blue-100 focus:ring-blue-500'
  }
})

const toggleRecording = async () => {
  if (isRecording.value) {
    status.value = 'transcribing'
    try {
      const audioBlob = await stopRecording()
      const transcribedText = await helpdeskStore.transcribeAudio(audioBlob)
      emit('transcription-complete', transcribedText)
      status.value = 'idle'
    } catch (error) {
      console.error('Error during transcription:', error)
      emit('error', 'Could not transcribe audio.')
      status.value = 'error'
      setTimeout(() => {
        if (status.value === 'error') status.value = 'idle'
      }, 3000)
    }
  } else {
    status.value = 'requesting_permission'
    try {
      await startRecording()
      status.value = 'recording'
    } catch (error) {
      console.error('Error starting recording:', error)
      emit('error', 'Microphone permission was denied.')
      status.value = 'error'
       setTimeout(() => {
        if (status.value === 'error') status.value = 'idle'
      }, 3000)
    }
  }
}
</script> 