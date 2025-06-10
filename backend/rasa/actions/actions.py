# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
import requests
import logging
import os

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

logger = logging.getLogger(__name__)

# Get the Ollama base URL from an environment variable for flexibility,
# defaulting to the local development setup.
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

class ActionLLMFallback(Action):
    def name(self) -> Text:
        return "action_llm_fallback"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Let the user know the bot is processing the request
        dispatcher.utter_message(response="utter_please_wait")

        # Get the last user message
        user_message = tracker.latest_message.get('text')

        # Construct a clear prompt for the LLM
        prompt = (
            "You are a helpful and creative assistant for the 'UCC Event Manager' application. "
            "Your primary goal is to answer user questions about using the application or about general topics. "
            "If you don't know the answer or the question is unrelated, just say that you cannot help with that. "
            f"Please provide a helpful and concise response to the following user query: '{user_message}'"
        )

        # Define the payload for the Ollama generate API
        payload = {
            "model": "deepseek-r1:8b",
            "prompt": prompt,
            "stream": False  # Get the full response at once
        }

        try:
            # Make the API call to the Ollama server
            response = requests.post(f"{OLLAMA_API_BASE}/api/generate", json=payload, timeout=45)
            response.raise_for_status()

            response_data = response.json()
            llm_response = response_data.get("response")

            if llm_response:
                dispatcher.utter_message(text=llm_response.strip())
            else:
                logger.error("Ollama response was empty.")
                dispatcher.utter_message(text="I'm sorry, I'm having trouble thinking of a response right now.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama fallback request failed: {e}")
            dispatcher.utter_message(text="I'm sorry, I couldn't connect to my advanced thinking module. Please try again later.")

        return [] 