# DSBot - Customer Service Chatbot API

A FastAPI-based customer service chatbot powered by Google Gemini AI. The chatbot is designed to handle customer inquiries about cleaning services with intelligent, context-aware responses.

## Features

- 🤖 **AI-Powered Responses**: Uses Google Gemini AI for intelligent, natural language responses
- 💬 **Conversation History**: Maintains chat context per user session
- 🔧 **Customizable Prompts**: Admin endpoints to customize the chatbot's personality and service profile
- 📝 **Multiple Service Profiles**: Support for different service types beyond cleaning
- 🚀 **FastAPI**: Modern, fast, and well-documented API framework
- 🔒 **Environment-based Configuration**: Secure API key management

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key (get yours at [Google AI Studio](https://makersuite.google.com/app/apikey))

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dawitsema/DSBot.git
   cd DSBot
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Google Gemini API key:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

## Running the API

### Development Mode

Start the server with auto-reload:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Production Mode

Run the server directly:

```bash
python main.py
```

Or use uvicorn with production settings:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Core Endpoints

#### `GET /` - Root
Get API information and available endpoints.

**Example**:
```bash
curl http://localhost:8000/
```

#### `GET /health` - Health Check
Check API health and configuration status.

**Example**:
```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "gemini_configured": true,
  "timestamp": "2024-01-15T12:00:00"
}
```

### Chat Endpoints

#### `POST /chat` - Send Message
Send a message to the chatbot and receive an AI-generated response.

**Request Body**:
```json
{
  "message": "What cleaning services do you offer?",
  "session_id": "optional-session-id"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your office cleaning rates?"}'
```

**Response**:
```json
{
  "response": "Our office cleaning rates start at $40-50 per hour...",
  "session_id": "session_1234567890",
  "timestamp": "2024-01-15T12:00:00"
}
```

#### `GET /chat/history/{session_id}` - Get Chat History
Retrieve conversation history for a specific session.

**Example**:
```bash
curl http://localhost:8000/chat/history/session_1234567890
```

**Response**:
```json
{
  "session_id": "session_1234567890",
  "history": [
    {
      "role": "User",
      "content": "What services do you offer?",
      "timestamp": "2024-01-15T12:00:00"
    },
    {
      "role": "Assistant",
      "content": "We offer residential cleaning, commercial cleaning...",
      "timestamp": "2024-01-15T12:00:01"
    }
  ],
  "message_count": 2
}
```

#### `DELETE /chat/history/{session_id}` - Clear Chat History
Clear conversation history for a specific session.

**Example**:
```bash
curl -X DELETE http://localhost:8000/chat/history/session_1234567890
```

### Admin Endpoints

#### `POST /admin/system-prompt` - Update System Prompt
Customize the chatbot's behavior by updating the system prompt.

**Request Body**:
```json
{
  "prompt": "You are a helpful assistant for a plumbing service...",
  "profile_name": "plumbing"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/admin/system-prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "You are a friendly customer service agent for QuickFix Plumbing Services...",
    "profile_name": "plumbing"
  }'
```

#### `GET /admin/system-prompt/{profile_name}` - Get System Prompt
Retrieve the system prompt for a specific profile.

**Example**:
```bash
curl http://localhost:8000/admin/system-prompt/default
```

#### `GET /admin/profiles` - List Profiles
List all available service profiles.

**Example**:
```bash
curl http://localhost:8000/admin/profiles
```

## Usage Examples

### Basic Chat Interaction

```python
import requests

# Start a conversation
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "What cleaning services do you offer?"}
)
data = response.json()
print(f"Bot: {data['response']}")
session_id = data['session_id']

# Continue the conversation with context
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "How much does deep cleaning cost?",
        "session_id": session_id
    }
)
data = response.json()
print(f"Bot: {data['response']}")
```

### Customizing the Service Profile

```python
import requests

# Create a new service profile for a restaurant
requests.post(
    "http://localhost:8000/admin/system-prompt",
    json={
        "profile_name": "restaurant",
        "prompt": """You are a customer service agent for Delicious Bites Restaurant.
        Help customers with:
        - Menu information
        - Reservations
        - Dietary restrictions
        - Hours of operation
        - Special events
        Be friendly and professional."""
    }
)
```

## Project Structure

```
DSBot/
├── main.py              # FastAPI application and endpoints
├── requirements.txt     # Python dependencies
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── xe.md              # Project description
```

## Configuration

### Environment Variables

- `GEMINI_API_KEY` (required): Your Google Gemini API key
- `GEMINI_MODEL` (optional): The Gemini model to use (default: `gemini-pro`)
  - Options: `gemini-pro`, `gemini-1.5-pro`, `gemini-1.5-flash`
- `ALLOWED_ORIGINS` (optional): Comma-separated list of allowed CORS origins (default: `*`)
  - For production, specify trusted domains: `https://yourdomain.com,https://app.yourdomain.com`

### Default System Prompt

The default system prompt is configured for a cleaning service business called "SparkleClean Services". You can customize this through the `/admin/system-prompt` endpoint.

## Important Notes

### Data Persistence

⚠️ **Warning**: The current implementation uses in-memory storage for conversation history and custom prompts. This means:

- All conversation history will be lost when the server restarts
- Custom service profiles will need to be recreated after restart

**For production use**, consider implementing persistent storage using:
- Redis for fast in-memory caching with persistence
- PostgreSQL or MySQL for relational data storage
- MongoDB for document-based storage

### Security Considerations

- CORS is configured to allow all origins by default (`*`). For production:
  - Set `ALLOWED_ORIGINS` environment variable to specific trusted domains
  - Example: `ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com`
- Admin endpoints (`/admin/*`) should be protected with authentication in production

## Features in Detail

### Conversation History

The API maintains conversation context per session, allowing for natural, multi-turn conversations. Each session is identified by a `session_id`:

- If you don't provide a `session_id`, a new session is automatically created
- Provide the same `session_id` in subsequent requests to maintain context
- Use the `/chat/history/{session_id}` endpoint to review past conversations
- Clear history with `/chat/history/{session_id}` DELETE request

### Multiple Service Profiles

You can create and manage multiple service profiles for different business types:

1. Use the default "cleaning" profile out of the box
2. Create custom profiles via `/admin/system-prompt`
3. Each profile has its own system prompt defining the service characteristics
4. Switch between profiles by updating the "default" profile or implementing profile-specific routing

## Error Handling

The API provides clear error messages:

- `503 Service Unavailable`: Gemini API key not configured
- `404 Not Found`: Session or profile doesn't exist
- `500 Internal Server Error`: Error generating AI response

## Development

### Adding New Features

1. Update the FastAPI app in `main.py`
2. Add new Pydantic models for request/response validation
3. Update this README with new endpoint documentation

### Testing

Test the API using:
- The interactive Swagger UI at `/docs`
- curl commands (see examples above)
- Python requests library
- Your favorite API testing tool (Postman, Insomnia, etc.)

## Troubleshooting

### "Gemini API key not configured"
- Make sure you've created a `.env` file
- Verify your API key is correct
- Restart the server after updating `.env`

### "Error generating response"
- Check your internet connection
- Verify your Gemini API key is valid and has quota
- Check the server logs for detailed error messages

## Future Enhancements

Potential improvements:

- [ ] Persistent storage (database) for conversation history
- [ ] User authentication and authorization
- [ ] Rate limiting for API endpoints
- [ ] WebSocket support for real-time chat
- [ ] Integration with messaging platforms (WhatsApp, Telegram, etc.)
- [ ] Analytics and conversation insights
- [ ] Multi-language support
- [ ] File upload support for customer attachments

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For questions or support, please open an issue on GitHub.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Google Gemini AI](https://ai.google.dev/)
