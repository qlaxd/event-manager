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
from datetime import datetime, timedelta
import dateparser
import re
import uuid
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, BotUttered, SlotSet

# Get backend API URL from environment variable, or use default
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://backend:8000/api/v1')
RASA_SERVICE_API_KEY = os.getenv('RASA_SERVICE_API_KEY', '')
OLLAMA_API_BASE = os.getenv('OLLAMA_API_BASE', 'http://ollama:11434')
DEFAULT_MODEL = os.getenv('OLLAMA_MODEL', 'llama3:8b')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a constant for the bot user ID
# This should be a UUID that corresponds to a real user in the database
# For development, you can create a dedicated "bot user" in the database
# and use its ID here
BOT_USER_ID = "00000000-0000-0000-0000-000000000000"  # Replace with a real user ID from your database

# Helper function to parse occurrence text into ISO format
def _parse_occurrence_text(occurrence_text: str = None) -> str:
    """Parse occurrence text into ISO format."""
    if not occurrence_text:
        # Default to now + 1 day at noon
        tomorrow_noon = datetime.now().replace(
            hour=12, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        return tomorrow_noon.isoformat()
    
    try:
        # Use dateparser to handle various date formats
        parsed_date = dateparser.parse(occurrence_text)
        if parsed_date:
            return parsed_date.isoformat()
    except Exception as e:
        logger.error(f"Error parsing occurrence text: {e}")
    
    # Default to tomorrow noon if parsing fails
    tomorrow_noon = datetime.now().replace(
        hour=12, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)
    return tomorrow_noon.isoformat()

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

        # Construct a prompt that includes the user's message
        prompt = user_message

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
            
        # Return UserUtteranceReverted to not influence further conversations
        return [UserUtteranceReverted()] 
    
class ActionCreateEventFromLlm(Action):
    """
    Custom action that creates an event from extracted entities.
    """
    def name(self) -> Text:
        return "action_create_event_from_llm"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Execute the action to create an event using extracted entities.
        
        Args:
            dispatcher: Dispatcher to send messages to the user
            tracker: Conversation tracker
            domain: Domain definition
            
        Returns:
            List of events to influence the conversation
        """
        # Extract entities from the latest message
        latest_message = tracker.latest_message
        entities = latest_message.get('entities', [])
        
        # Log all extracted entities for debugging
        logger.info(f"All extracted entities: {entities}")
        
        # Create a dictionary to store the extracted values
        extracted_data = {}
        for entity in entities:
            entity_type = entity.get('entity')
            entity_value = entity.get('value')
            if entity_type and entity_value:
                extracted_data[entity_type] = entity_value
                
        # Get extracted entities from slots or extracted data
        title = tracker.get_slot("event_title") or extracted_data.get("event_title")
        description = tracker.get_slot("event_description") or extracted_data.get("event_description")
        occurrence_text = tracker.get_slot("event_occurrence_text") or extracted_data.get("event_occurrence_text")
        
        # If no title was extracted by the LLM, try to extract it from the user message
        user_message = latest_message.get('text', '')
        if not title:
            # Clean up common prefixes that shouldn't be part of the title
            title_patterns = [
                # Match "create an event titled [TITLE]" pattern - better pattern with word boundary
                r'(?:create|make|add|schedule)(?:\s+an?)?(?:\s+event)?(?:\s+titled)\s+([\w\s]+?)(?:\s+(?:for|on|at|tomorrow|next)|$)',
                
                # Match "create an event for [TITLE]" pattern
                r'(?:create|make|add|schedule)(?:\s+an?)?(?:\s+event)?(?:\s+for)\s+([\w\s]+?)(?:\s+(?:on|at|tomorrow|next)|$)',
                
                # Match simple "dinner with X" pattern that's likely an event title
                r'\b((?:dinner|lunch|breakfast|meeting|appointment|date|coffee|drinks|party|concert|movie|show)\s+(?:with|for|at|in)\s+[\w\s]+)\b',
                
                # More general patterns
                r'event\s+(?:for|titled|named)\s+([\w\s]+?)(?:\s+(?:on|at|tomorrow|next)|$)',
                r'esemény\s+(?:a|az|ezt)?\s+([\w\s]+?)(?:\s+(?:on|at|tomorrow|next)|$)'
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match and match.group(1):
                    title = match.group(1).strip()
                    break
        
        # If no description was extracted by the LLM, try to extract it from the user message
        if not description and "description" in user_message.lower():
            description_patterns = [
                r'description(?:\s+(?:that|which))?\s+(?:says|tells|is)?\s+([\w\s,.]+?)(?:$|\.|\n)',
                r'with\s+(?:a|the)?\s+description(?:\s+(?:that|which))?\s+([\w\s,.]+?)(?:$|\.|\n)'
            ]
            
            for pattern in description_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match and match.group(1):
                    description = match.group(1).strip()
                    break
        
        # If no occurrence text was extracted by the LLM, try to extract it from the user message
        if not occurrence_text:
            time_patterns = [
                r'(?:on|at|for)\s+(tomorrow|next\s+\w+|\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?\w+|\w+\s+\d{1,2}(?:st|nd|rd|th)?)\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
                r'(tomorrow|next\s+\w+|\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?\w+|\w+\s+\d{1,2}(?:st|nd|rd|th)?)\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
                r'(?:at|for)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)(?:\s+(?:on|next|tomorrow)\s+(tomorrow|next\s+\w+|\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?\w+|\w+\s+\d{1,2}(?:st|nd|rd|th)?))?'
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    if match.group(2):
                        occurrence_text = f"{match.group(1)} at {match.group(2)}"
                    else:
                        occurrence_text = match.group(1)
                    break
        
        # Clean up the title if it contains "titled" or other prefixes
        if title:
            title_prefixes = ["titled ", "for ", "create ", "event ", "an event ", "a "]
            for prefix in title_prefixes:
                if title.lower().startswith(prefix):
                    title = title[len(prefix):].strip()
            
            # Additional cleanup: if the title ends with "for" or similar prepositions, remove them
            title_suffixes = [" for", " on", " at", " in"]
            for suffix in title_suffixes:
                if title.lower().endswith(suffix):
                    title = title[:-len(suffix)].strip()
        
        # Log the extracted entities
        logger.info(f"Extracted entities for event creation: title='{title}', description='{description}', occurrence='{occurrence_text}'")
        
        # If no title was extracted, ask for clarification
        if not title:
            dispatcher.utter_message(response="utter_ask_event_title")
            return []
        
        # Parse the occurrence text into ISO format
        occurrence_iso = _parse_occurrence_text(occurrence_text)
        
        # Create the event using either the admin API key or a system user account
        # First, try to create an event via the admin API
        try:
            # Admin API approach - we need to use a service API key with admin privileges
            admin_payload = {
                "title": title,
                "description": description or f"Esemény létrehozva a chatbot által ekkor: {datetime.now().isoformat()}",
                "occurrence": occurrence_iso,
                "user_id": tracker.sender_id  # Use the requesting user's ID instead of BOT_USER_ID
            }
            
            admin_headers = {
                "Content-Type": "application/json",
                "X-Service-API-Key": RASA_SERVICE_API_KEY
            }
            
            logger.info(f"Making admin API request to create event for user {tracker.sender_id}")
            
            # Make the API call
            response = requests.post(
                f"{BACKEND_API_URL}/events/", 
                json=admin_payload, 
                headers=admin_headers,
                timeout=10
            )
            
            # Log the response for debugging
            logger.info(f"API response status: {response.status_code}")
            logger.info(f"API response content: {response.text[:500]}")
            
            response.raise_for_status()
            
            # Log the successful event creation
            logger.info(f"Event created via agent for user {tracker.sender_id} with title '{title}'")
            
            # Return a success message to the user
            dispatcher.utter_message(response="utter_event_created_by_agent", event_title=title)
            
            # Clear the slots after successful event creation
            return [
                SlotSet("event_title", None),
                SlotSet("event_description", None),
                SlotSet("event_occurrence_text", None)
            ]
            
        except requests.exceptions.RequestException as e:
            # Log the error details
            logger.error(f"Agentic event creation API call failed for user {tracker.sender_id}: {e}")
            
            # Add more detailed error information if available
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text[:500]}")
                
                # Check if we need to create a system user first
                if e.response.status_code == 409 and 'database_error' in e.response.text:
                    logger.error("Foreign key constraint violation - need to create system user first")
                    # You can add logic here to create a system user if needed
                
            # Return a failure message to the user
            dispatcher.utter_message(response="utter_event_creation_failed")
            
            # Don't clear slots on error to allow retrying
            return []
    
class ActionCreateEvent(Action):
    def name(self) -> Text:
        return "action_create_event"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="I'm sorry, I don't have specific information about that. As the UCC Event Manager assistant, I can help with creating and managing events. How can I assist you with event management today?") 
        return [UserUtteranceReverted()] 
    
class ActionGetEvent(Action):
    def name(self) -> Text:
        return "action_get_event"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="I'm sorry, I don't have specific information about that. As the UCC Event Manager assistant, I can help with creating and managing events. How can I assist you with event management today?") 
        return [UserUtteranceReverted()] 
