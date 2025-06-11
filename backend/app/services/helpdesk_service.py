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
        
        Waits for the complete response from the LLM, with a reasonable timeout.
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
            # Increased timeout to 60 seconds to allow for LLM processing
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(rasa_webhook_url, json=rasa_payload)
                response.raise_for_status()
                rasa_responses = response.json()
        except httpx.TimeoutException:
            logger.error(
                "Request timed out after 60 seconds waiting for LLM response",
                user_id=user_id,
                message=request.message
            )
            
            # Return a timeout message
            return ChatMessageResponse(
                response="I'm sorry, but it's taking longer than expected to process your request. Please try again later.",
                session_id=request.session_id or user_id,
            )
            
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