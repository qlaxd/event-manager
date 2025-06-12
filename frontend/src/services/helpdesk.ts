import apiClient from './api'
import type { 
  ChatMessageRequest, 
  ChatMessageResponse,
  EscalateRequest,
  EscalateResponse
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
}

export default new HelpdeskService() 