"""Service layer for helpdesk and chatbot integration."""
import httpx
import structlog
from fastapi import HTTPException, status
from typing import Optional, Dict
import uuid
import asyncio

from app.core.config import settings
from schemas.helpdesk import ChatMessageRequest, ChatMessageResponse

logger = structlog.get_logger(__name__)

# In-memory store for pending responses (in production, use Redis or similar)
pending_responses: Dict[str, ChatMessageResponse] = {}

class HelpdeskService:
    """Handles communication with the Rasa chatbot service."""

    @staticmethod
    async def talk_to_bot(user_id: str, request: ChatMessageRequest) -> ChatMessageResponse:
        """
        Sends a message to the Rasa server and gets a response.
        
        If the message requires LLM processing, it will return an immediate 
        response with processing=True and store the response_id for polling.
        """
        if not settings.RASA_URL:
            logger.error("RASA_URL is not configured. Cannot connect to chatbot.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Helpdesk service is currently unavailable.",
            )

        rasa_payload = {
            "sender": user_id,
            "message": request.message,
        }
        
        rasa_webhook_url = f"{settings.RASA_URL}/webhooks/rest/webhook"

        try:
            # Increased timeout to 30 seconds to allow for immediate responses
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(rasa_webhook_url, json=rasa_payload)
                response.raise_for_status()
                rasa_responses = response.json()
        except httpx.TimeoutException:
            # If we hit a timeout, assume it's an LLM request being processed
            response_id = str(uuid.uuid4())
            logger.info(
                "Request timed out, likely an LLM-based response being processed",
                user_id=user_id,
                response_id=response_id
            )
            
            # Create and store a pending response
            pending_response = ChatMessageResponse(
                response="I'm processing your request. This might take a moment...",
                session_id=request.session_id or user_id,
                processing=True,
                response_id=response_id
            )
            pending_responses[response_id] = pending_response
            
            # Return the pending response to the client
            return pending_response
            
        except httpx.RequestError as e:
            logger.error(
                "Could not connect to Rasa server",
                url=rasa_webhook_url,
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The chatbot service is temporarily down.",
            )
        except Exception as e:
            logger.error(
                "An unexpected error occurred while communicating with Rasa",
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing your message.",
            )

        if not rasa_responses:
            return ChatMessageResponse(
                response="I'm sorry, I couldn't understand that. Could you please rephrase?",
                session_id=request.session_id or user_id,
            )

        # Extract the primary text response and any quick replies
        bot_text_response = ""
        quick_replies = []
        for r in rasa_responses:
            if "text" in r:
                bot_text_response += r["text"] + " "
            if "buttons" in r:
                quick_replies.extend([button["title"] for button in r["buttons"]])
        
        return ChatMessageResponse(
            response=bot_text_response.strip(),
            session_id=request.session_id or user_id,
            quick_replies=quick_replies if quick_replies else None,
        )
    
    @staticmethod
    async def get_pending_response(response_id: str) -> Optional[ChatMessageResponse]:
        """
        Retrieves a pending response by its ID.
        
        Returns None if the response doesn't exist.
        """
        return pending_responses.get(response_id) 