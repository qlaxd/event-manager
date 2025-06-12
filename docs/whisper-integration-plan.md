# Whisper Voice-to-Text Integration Plan

## 1. Overview
This document outlines the development plan for integrating OpenAI's Whisper API into the chatbot interface. This feature will allow users to provide input via voice, which will be transcribed into text and placed in the chat input box. The user can then review and send the message.

The primary goal is to enhance accessibility and user experience by providing an alternative to typing. A microphone icon will be added to the chat input bar to provide an intuitive entry point to this functionality.

**User Story Covered:**
- **US-012 (Voice Input)**: As a user, I want to speak my message instead of typing it, so I can communicate more easily and quickly with the chatbot.

---

## 2. Technology & Architecture Recommendations

- **Frontend**:
  - **Audio Recording**: The browser's native `MediaRecorder` API will be used to capture audio from the user's microphone. This avoids external dependencies and is supported by all modern browsers.
  - **Data Transfer**: The recorded audio will be sent to the backend as a `Blob` within a `multipart/form-data` request using `axios` or `fetch`.
  - **UI**: A new UI component will be created to house the microphone icon and manage visual states (e.g., idle, recording, processing, error).

- **Backend**:
  - **API Framework**: FastAPI's `UploadFile` will be used to efficiently handle the incoming audio file.
  - **OpenAI Integration**: The official `openai` Python library will be used to interact with the Whisper API.
  - **Configuration**: The `OPENAI_API_KEY` will be managed securely via environment variables and the application's configuration system.

---

## Phase 1: Backend API Development

**Objective**: Create a secure endpoint to handle audio transcription requests.

### Task 1.1: Update Configuration & Dependencies
- **File**: `app/core/config.py`
  - **Action**: Add `OPENAI_API_KEY: str` to the `Settings` class to load the key from environment variables.
- **File**: `.env.example`
  - **Action**: Add `OPENAI_API_KEY="your_openai_api_key_here"` to the example environment file.
- **File**: `requirements.txt`
  - **Action**: Add the `openai` library: `openai>=1.3.0`.

### Task 1.2: Pydantic Schemas
- **File**: `app/schemas/helpdesk.py`
- **Action**: Define a Pydantic schema for the transcription response.
- **Details**: This schema defines the API's response contract.

  ```python
  # In app/schemas/helpdesk.py
  # ... existing imports
  class TranscriptionResponse(BaseModel):
      text: str
  ```

### Task 1.3: OpenAI Client Service
- **File**: `app/clients/openai_client.py` (New File)
- **Action**: Create a dedicated client to encapsulate Whisper API calls.
- **Details**: This promotes separation of concerns and simplifies testing.

  ```python
  # In app/clients/openai_client.py
  import openai
  from fastapi import UploadFile
  from app.core.config import settings

  class OpenAIClient:
      def __init__(self):
          self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

      async def transcribe_audio(self, file: UploadFile) -> str:
          # Note: The 'file' parameter for transcription needs a file-like object with a name.
          # FastAPI's UploadFile works perfectly here.
          transcription = await self.client.audio.transcriptions.create(
              model="whisper-1",
              file=file.file,
          )
          return transcription.text
  ```

### Task 1.4: Enhance Helpdesk Service
- **File**: `app/services/helpdesk_service.py`
- **Action**: Add a `transcribe_audio_input` method.
- **Details**: This service method will orchestrate the transcription process.

  ```python
  # In app/services/helpdesk_service.py
  from app.clients.openai_client import OpenAIClient
  from fastapi import UploadFile, HTTPException, status
  # ... other imports

  class HelpdeskService:
      # ... existing methods
      
      async def transcribe_audio_input(self, file: UploadFile) -> str:
          if not file.content_type.startswith("audio/"):
              raise HTTPException(
                  status_code=status.HTTP_400_BAD_REQUEST,
                  detail="Invalid file type. Please upload an audio file.",
              )
          
          openai_client = OpenAIClient()
          try:
              transcribed_text = await openai_client.transcribe_audio(file)
              return transcribed_text
          except Exception as e:
              # Log the exception from OpenAI
              logger.error(f"Whisper API error: {e}")
              raise HTTPException(
                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                  detail="Could not process the audio file.",
              )

  ```

### Task 1.5: API Endpoint Implementation
- **File**: `app/api/v1/endpoints/helpdesk.py`
- **Action**: Create the `POST /helpdesk/transcribe` endpoint.
- **Details**: This endpoint will be protected and require authentication.

  ```python
  # In app/api/v1/endpoints/helpdesk.py
  from fastapi import UploadFile, File
  # ... other imports

  @router.post(
      "/transcribe",
      response_model=schemas.TranscriptionResponse,
      status_code=status.HTTP_200_OK,
      summary="Transcribe user audio to text",
      description="Accepts an audio file and returns the transcribed text using OpenAI Whisper.",
      tags=["Helpdesk"],
  )
  async def transcribe_audio(
      file: UploadFile = File(...),
      db: AsyncSession = Depends(get_db),
      current_user: User = Depends(get_current_active_user),
  ):
      helpdesk_service = HelpdeskService(db)
      transcribed_text = await helpdesk_service.transcribe_audio_input(file)
      return schemas.TranscriptionResponse(text=transcribed_text)
  ```

---

## Phase 2: Frontend Implementation

**Objective**: Build the user-facing microphone component and connect it to the new backend endpoint.

### Task 2.1: UI Component
- **File**: `frontend/src/components/chat/VoiceRecorder.vue` (New File)
- **Action**: Create a Vue component for the microphone button.
- **Details**: This component will manage all its internal state:
  - `status`: 'idle', 'requesting_permission', 'recording', 'transcribing', 'error'.
  - It will display a microphone icon that changes based on the status.
  - It will handle user interactions (click to start/stop recording).
  - It will emit the final transcribed text to its parent.

### Task 2.2: Audio Recording Logic
- **File**: `frontend/src/composables/useAudioRecorder.js` (New File)
- **Action**: Create a composable to encapsulate audio recording logic.
- **Details**:
  - Request microphone permission using `navigator.mediaDevices.getUserMedia`.
  - Initialize `MediaRecorder` with the audio stream.
  - Handle `start()`, `stop()`, and `ondataavailable` events.
  - Collect audio chunks and create a `Blob` when recording stops.

### Task 2.3: State Management (Pinia)
- **File**: `frontend/src/stores/chat.ts` (or equivalent)
- **Action**: Add state and an action for transcription.
- **Details**:
  - **State**: `isTranscribing: boolean`, `transcriptionError: string | null`.
  - **Action**: `async function transcribeAudio(audioBlob: Blob)`:
    - Sets `isTranscribing` to `true`.
    - Creates a `FormData` object and appends the audio blob.
    - Makes a `POST` request to the `/api/v1/helpdesk/transcribe` endpoint.
    - On success, returns the transcribed text.
    - On failure, sets `transcriptionError`.
    - Sets `isTranscribing` to `false` in a `finally` block.

### Task 2.4: Integrate into Chat View
- **File**: `frontend/src/views/ChatView.vue` (or equivalent component with the input bar)
- **Action**: Integrate the `VoiceRecorder` component.
- **Details**:
  - Place the `<VoiceRecorder />` component next to the text input field.
  - Listen for the `transcription-complete` event from the component.
  - When the event is received, update the `v-model` of the chat text input with the transcribed text.

---

## Phase 3: Testing

**Objective**: Ensure the feature is reliable, secure, and functions correctly end-to-end.

### Task 3.1: Backend Integration Tests
- **File**: `tests/api/v1/test_helpdesk_endpoints.py`
- **Action**: Add tests for the `/transcribe` endpoint.
- **Details**:
  - **Success Case**:
    - Mock the `OpenAIClient.transcribe_audio` method to return a sample text.
    - Call the endpoint with a valid user token and a sample audio file (`.mp3` or `.wav`).
    - Assert a `200 OK` response and that the response body contains the mocked text.
  - **Security Case**:
    - Test that an unauthenticated request fails with `401 UNAUTHORIZED`.
  - **Validation Case**:
    - Test that a request with a non-audio file (e.g., `text/plain`) fails with `400 BAD REQUEST`.
  - **API Failure Case**:
    - Mock the `OpenAIClient.transcribe_audio` to raise an exception.
    - Assert the endpoint returns `500 INTERNAL SERVER_ERROR`.

### Task 3.2: Frontend Component Tests
- **File**: `tests/components/VoiceRecorder.spec.ts`
- **Action**: Write unit tests for the `VoiceRecorder` component.
- **Details**:
  - Mock the `useAudioRecorder` composable and the Pinia store action.
  - Test that the component's UI changes correctly based on its status prop.
  - Simulate a click and verify that the correct recording functions are called.
  - Simulate a successful transcription and verify that the `transcription-complete` event is emitted with the correct text.
  - Simulate an error and verify that an error message is displayed.

---

## Phase 4: Finalization and Hardening

- **Error Handling (Frontend)**:
  - Implement clear user feedback for microphone permission denial.
  - Show a toast notification or inline message if transcription fails.
  - Handle cases where no audio is recorded (e.g., user clicks start then immediately stop).
- **UI/UX Refinements**:
  - Add tooltips to the microphone icon to explain its state.
  - Use subtle animations to indicate the "recording" and "transcribing" states.
- **API Documentation**:
  - Review the auto-generated OpenAPI docs for the `/transcribe` endpoint. Ensure the description, summary, and schema are clear and accurate.
- **Rate Limiting**:
  - Apply a rate limit (`slowapi`) to the `/transcribe` endpoint to prevent abuse (e.g., "30 requests per 5 minutes per user"). This is crucial for controlling OpenAI API costs.
- **Logging**:
  - Enhance `HelpdeskService` logging to record when a transcription is requested and when it succeeds or fails, including `user_id`.

By following this plan, the development team can systematically build and integrate a high-quality voice input feature, significantly improving the chatbot's user interface and accessibility. 