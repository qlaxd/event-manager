import { ref } from 'vue'

export function useAudioRecorder() {
  const isRecording = ref(false)
  const mediaRecorder = ref<MediaRecorder | null>(null)
  const audioChunks = ref<Blob[]>([])

  const startRecording = async (): Promise<void> => {
    if (isRecording.value) return

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder.value = new MediaRecorder(stream)
      audioChunks.value = []

      mediaRecorder.value.ondataavailable = (event) => {
        audioChunks.value.push(event.data)
      }

      mediaRecorder.value.onstop = () => {
        isRecording.value = false
        // stop microphone tracks
        stream.getTracks().forEach(track => track.stop());
      }

      mediaRecorder.value.start()
      isRecording.value = true
    } catch (err) {
      console.error('Error accessing microphone:', err)
      throw new Error('Microphone permission denied.')
    }
  }

  const stopRecording = (): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      if (!mediaRecorder.value || !isRecording.value) {
        return reject('Not recording.')
      }

      mediaRecorder.value.onstop = () => {
        const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
        audioChunks.value = []
        isRecording.value = false
        if (mediaRecorder.value) {
            mediaRecorder.value.stream.getTracks().forEach(track => track.stop());
        }
        resolve(audioBlob)
      }

      mediaRecorder.value.stop()
    })
  }

  return {
    isRecording,
    startRecording,
    stopRecording,
  }
}
