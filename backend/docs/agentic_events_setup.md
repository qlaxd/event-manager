# Agentic Events Feature Setup Guide

This guide will help you set up and test the agentic events feature, which allows users to create events by conversing naturally with the chatbot.

## Prerequisites

- Docker and Docker Compose installed
- Git repository cloned

## Setup Steps

### 1. Environment Variables

Create or update your `.env` file in the `backend` directory with the following variables:

```bash
# Rasa Service settings (add these to your existing .env file)
RASA_SERVICE_API_KEY=your-secure-api-key
OLLAMA_API_BASE=http://ollama:11434
```

Generate a secure random key for `RASA_SERVICE_API_KEY`:
```bash
openssl rand -hex 32
```

### 2. Rebuild and Start Services

```bash
cd backend
docker-compose down
docker-compose build action-server rasa backend
docker-compose up -d
```

### 3. Train the Rasa Model

```bash
docker-compose exec rasa rasa train
```

### 4. Test the Feature

You can test the feature in several ways:

#### Using the Rasa Shell

```bash
docker-compose exec rasa rasa shell
```

Example conversation:
```
Your input -> csinálj egy eventet a hétvégi grillezésnek, hogy kell krumpli meg csevap
```

#### Using the API

Send a message to the Rasa API:

```bash
curl -X POST \
  http://localhost:5005/webhooks/rest/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "sender": "user123",
    "message": "csinálj egy eventet a hétvégi grillezésnek, hogy kell krumpli meg csevap"
  }'
```

#### Running Tests

```bash
docker-compose exec rasa rasa test
```

## Troubleshooting

### Common Issues

1. **API Key Authentication Failures**
   - Ensure the `RASA_SERVICE_API_KEY` value is the same in both the Rasa action server and backend environments
   - Check the logs for any authentication errors

2. **Entity Extraction Issues**
   - If entities aren't being properly extracted, you may need to update the examples in the LLM Entity Extractor configuration
   - Add more examples to the `nlu.yml` file for the `create_event_unstructured` intent

3. **API Connection Issues**
   - Check that the `BACKEND_API_URL` is correctly set in the action server environment
   - Verify network connectivity between the containers

### Viewing Logs

```bash
# View Rasa logs
docker-compose logs -f rasa

# View Action Server logs
docker-compose logs -f action-server

# View Backend logs
docker-compose logs -f backend
```

## Extending the Feature

To extend this feature:

1. Add more entity examples in `config.yml` to improve extraction
2. Enhance the custom action to handle more complex date/time expressions
3. Add more training examples in `nlu.yml` to recognize different ways users might ask to create events

## Security Considerations

- The API key should be kept secure and rotated regularly
- Communication between the action server and backend is internal to the Docker network
- User IDs are passed securely from the chatbot to the backend

For more information, refer to the [development plan documentation](backend/dev/agentic-events-development-plan.md). 