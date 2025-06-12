"""
Helpdesk endpoints for UCC Event Manager.
Provides an interface to the chatbot.
"""
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
import structlog

from app.models.user import User
from app.core.security import get_current_active_user
from schemas.helpdesk import (
    ChatMessageRequest,
    ChatMessageResponse,
    TranscriptionResponse,
)
from app.services.helpdesk_service import HelpdeskService

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe user audio to text",
    description="Accepts an audio file and returns the transcribed text using OpenAI Whisper.",
    tags=["Helpdesk"],
)
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    """
    Handles audio file transcription.

    - **file**: The audio file (e.g., .mp3, .wav) to be transcribed.
    """
    transcribed_text = await HelpdeskService.transcribe_audio_input(file)
    logger.info(
        "Audio transcription successful for user.",
        user_id=str(current_user.id),
    )
    return TranscriptionResponse(text=transcribed_text)

@router.post(
    "/chat",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the helpdesk chatbot",
    description="Allows an authenticated user to send a message to the Rasa-powered chatbot and receive a response.",
    tags=["Helpdesk"],
)
async def send_chat_message(
    chat_request: ChatMessageRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Handles a user's message to the chatbot.

    - **message**: The text message from the user.
    - **session_id**: An optional session ID to maintain conversation context.
    """
    response = await HelpdeskService.talk_to_bot(user_id=str(current_user.id), request=chat_request)
    return response

# TODO: Implement escalation and chat history endpoints

# TODO: Implement helpdesk endpoints
# - POST /helpdesk/escalate
# - GET /helpdesk/sessions/{session_id}/messages
# - POST /helpdesk/sessions
# - DELETE /helpdesk/sessions/{session_id}
# - POST /helpdesk/voice/session (bonus)
# - POST /helpdesk/voice/process (bonus) 