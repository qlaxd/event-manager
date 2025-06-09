"""
Helpdesk endpoints for UCC Event Manager.
Provides an interface to the chatbot.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_current_active_user
from schemas.helpdesk import ChatMessageRequest, ChatMessageResponse
from app.services.helpdesk_service import HelpdeskService

router = APIRouter()

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
# - POST /helpdesk/chat
# - POST /helpdesk/escalate
# - GET /helpdesk/sessions/{session_id}/messages
# - POST /helpdesk/sessions
# - DELETE /helpdesk/sessions/{session_id}
# - POST /helpdesk/voice/session (bonus)
# - POST /helpdesk/voice/process (bonus) 