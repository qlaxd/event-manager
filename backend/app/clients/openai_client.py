import openai
from fastapi import UploadFile
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class OpenAIClient:
    """A client for interacting with the OpenAI API."""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment.")
        try:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    async def transcribe_audio(self, file: UploadFile) -> str:
        """
        Transcribes audio using the Whisper API.

        Args:
            file: An UploadFile object containing the audio.

        Returns:
            The transcribed text.
        
        Raises:
            Exception: If the transcription fails.
        """
        try:
            # The 'file' parameter for transcription needs a file-like object.
            # FastAPI's UploadFile provides a file-like 'file' attribute.
            transcription = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=file.file,
            )
            return transcription.text
        except openai.APIError as e:
            logger.error(f"OpenAI API error during transcription: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during transcription: {e}")
            raise 