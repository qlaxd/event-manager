import apiClient from './api'
import type { 
  ChatMessageRequest, 
  ChatMessageResponse,
  EscalateRequest,
  EscalateResponse,
  TranscriptionResponse
} from '@/types'

class HelpdeskService {
  async sendMessage(data: ChatMessageRequest): Promise<ChatMessageResponse> {
    const response = await apiClient.post<ChatMessageResponse>('/helpdesk/chat', data)
    return response.data
  }

  async escalate(data: EscalateRequest): Promise<EscalateResponse> {
    const response = await apiClient.post<EscalateResponse>('/helpdesk/escalate', data)
    return response.data
  }

  async transcribeAudio(audioBlob: Blob): Promise<TranscriptionResponse> {
    const formData = new FormData()
    formData.append('file', audioBlob, 'recording.webm')

    const response = await apiClient.post<TranscriptionResponse>('/helpdesk/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }
}

export default new HelpdeskService() 