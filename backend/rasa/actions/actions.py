# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
import requests
import logging
import os
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, BotUttered

logger = logging.getLogger(__name__)

# Get the Ollama base URL from an environment variable for flexibility,
# defaulting to the local development setup.
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://ollama:11434")
# Use our LLM model as the default model
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")

# A simple in-memory cache to store pending responses
# In a production environment, this should be replaced with Redis or similar
pending_responses = {}
executor = ThreadPoolExecutor(max_workers=5)

class ActionLLMFallback(Action):
    def name(self) -> Text:
        return "action_llm_fallback"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the last user message
        user_message = tracker.latest_message.get('text')
        user_id = tracker.sender_id
        
        logger.info(f"Redirecting to Ollama LLM: '{user_message}'")

        # Let the user know the bot is processing the request immediately
        dispatcher.utter_message(text="I'm processing your request. This might take a moment...")
        
        # Start the LLM request in the background
        executor.submit(self.get_llm_response, user_message, user_id, dispatcher)
        
        # Return immediately with UserUtteranceReverted to not influence further conversations
        return [UserUtteranceReverted()]
    
    def get_llm_response(self, user_message: str, user_id: str, dispatcher: CollectingDispatcher) -> None:
        """Process the LLM request in the background and send the response when ready."""
        
        # Construct a clear prompt for the LLM
        prompt = (
            "I'm sorry, but I don't have specific information about that. As the UCC Event Manager assistant, "
            "I can help you with creating, managing, and attending events. I can assist with registration, "
            "scheduling, and other event-related tasks. How can I help you with event management today?"
        )

        # Define the payload for the Ollama generate API
        payload = {
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False  # Get the full response at once
        }

        try:
            # Check if Ollama is available
            health_url = f"{OLLAMA_API_BASE}/"
            try:
                health_check = requests.head(health_url, timeout=5)
                if health_check.status_code != 200:
                    logger.error(f"Ollama server health check failed with status {health_check.status_code}")
                    raise Exception("Ollama server health check failed")
            except requests.exceptions.RequestException as he:
                logger.error(f"Could not connect to Ollama server for health check: {he}")
                raise Exception("Ollama server unavailable")
            
            # Log the request URL for debugging
            request_url = f"{OLLAMA_API_BASE}/api/generate"
            logger.info(f"Sending request to Ollama API: {request_url}")
            
            # Make the API call to the Ollama server with a longer timeout
            response = requests.post(request_url, json=payload, timeout=60)
            
            # Log the response status and headers for debugging
            logger.info(f"Ollama API response status: {response.status_code}")
            logger.info(f"Ollama API response headers: {response.headers}")
            
            response.raise_for_status()

            # Log the raw response for debugging
            logger.debug(f"Ollama API raw response: {response.text[:500]}...")
            
            response_data = response.json()
            llm_response = response_data.get("response")

            if llm_response:
                logger.info(f"Successful LLM response received (first 100 chars): {llm_response[:100]}...")
                # Send the LLM response directly to the user through the dispatcher
                dispatcher.utter_message(text=llm_response.strip())
            else:
                logger.error(f"Ollama response was empty or missing 'response' field. Full response: {json.dumps(response_data)}")
                dispatcher.utter_message(text="I'm sorry, I'm having trouble thinking of a response right now.")

        except Exception as e:
            logger.error(f"Ollama fallback request failed: {e}")
            # Add more detailed error information
            if isinstance(e, requests.exceptions.RequestException) and hasattr(e, 'response') and e.response:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text[:500]}")
            
            # Provide a more user-friendly fallback response
            dispatcher.utter_message(text="I'm sorry, I don't have specific information about that. As the UCC Event Manager assistant, I can help with creating and managing events. How can I assist you with event management today?") 