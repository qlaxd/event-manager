"""Pydantic schemas for helpdesk and chatbot interactions."""
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

class ChatMessageRequest(BaseModel):
    """Schema for a user sending a message to the chatbot."""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="The ongoing conversation session ID.")

class ChatMessageResponse(BaseModel):
    """Schema for the chatbot's response."""
    response: str
    session_id: str
    confidence: Optional[float] = None
    escalation_suggested: bool = False
    quick_replies: Optional[List[str]] = None

class EscalationRequest(BaseModel):
    """Schema for escalating a chat to a human agent."""
    session_id: str
    reason: str = Field(..., max_length=255)
    message: str = Field(..., max_length=2000)

class EscalationResponse(BaseModel):
    """Schema for the response after an escalation request."""
    ticket_id: str
    message: str
    estimated_wait_time: Optional[str] = None 