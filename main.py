"""
Customer Service Chatbot API using FastAPI and Google Gemini

This API provides customer service chatbot functionality powered by Google's Gemini AI.
The bot specializes in providing information about cleaning services.
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Customer Service Chatbot API",
    description="AI-powered customer service chatbot for cleaning services",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini
# Set your GEMINI_API_KEY in .env file or as an environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found. Please set it in .env file or environment variables.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Default system prompt for cleaning agent service
DEFAULT_SYSTEM_PROMPT = """You are a friendly and professional customer service agent for SparkleClean Services, 
a premium cleaning service company. Your role is to help customers with:

1. Information about our cleaning services:
   - Residential cleaning (homes, apartments)
   - Commercial cleaning (offices, retail spaces)
   - Deep cleaning services
   - Move-in/move-out cleaning
   - Post-construction cleaning
   - Window cleaning
   - Carpet and upholstery cleaning

2. Pricing information:
   - Basic cleaning: $25-35/hour
   - Deep cleaning: $40-50/hour
   - Commercial rates: Custom quotes based on space size
   - Special services: Contact for detailed pricing

3. Booking and scheduling:
   - We operate Monday-Saturday, 8 AM - 6 PM
   - Same-day service available for urgent requests
   - Flexible scheduling options

4. Service areas:
   - We serve the greater metropolitan area
   - Contact us for availability in your specific location

5. Our commitment:
   - Eco-friendly cleaning products
   - Trained and insured staff
   - 100% satisfaction guarantee
   - Flexible cancellation policy

Always be helpful, courteous, and provide accurate information. If you don't know something, 
politely tell the customer you'll need to check with management and they can contact us directly 
at contact@sparkleclean.example or call (555) 123-4567.
"""

# In-memory storage for conversation history and custom prompts
conversation_history: Dict[str, List[Dict[str, str]]] = {}
custom_prompts: Dict[str, str] = {}


# Pydantic models for request/response validation
class ChatMessage(BaseModel):
    """Model for a chat message"""
    message: str = Field(..., description="The user's message to the chatbot")
    session_id: Optional[str] = Field(None, description="Session ID to maintain conversation context")


class ChatResponse(BaseModel):
    """Model for chatbot response"""
    response: str = Field(..., description="The chatbot's response")
    session_id: str = Field(..., description="Session ID for this conversation")
    timestamp: str = Field(..., description="Response timestamp")


class SystemPromptUpdate(BaseModel):
    """Model for updating system prompt"""
    prompt: str = Field(..., description="New system prompt for the chatbot")
    profile_name: Optional[str] = Field("default", description="Name for this service profile")


class SystemPromptResponse(BaseModel):
    """Model for system prompt response"""
    message: str = Field(..., description="Confirmation message")
    profile_name: str = Field(..., description="Profile name")
    prompt: str = Field(..., description="The system prompt")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Customer Service Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "POST /chat": "Send a message to the chatbot",
            "GET /chat/history/{session_id}": "Get conversation history for a session",
            "DELETE /chat/history/{session_id}": "Clear conversation history for a session",
            "POST /admin/system-prompt": "Update the system prompt (admin)",
            "GET /admin/system-prompt/{profile_name}": "Get system prompt for a profile",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    gemini_configured = GEMINI_API_KEY is not None
    return {
        "status": "healthy",
        "gemini_configured": gemini_configured,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Send a message to the chatbot and get a response.
    
    The chatbot maintains conversation context per session_id.
    If no session_id is provided, a new session will be created.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
        )
    
    try:
        # Generate or use provided session ID
        session_id = chat_message.session_id or f"session_{datetime.utcnow().timestamp()}"
        
        # Initialize conversation history for new sessions
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Get the system prompt (custom or default)
        system_prompt = custom_prompts.get("default", DEFAULT_SYSTEM_PROMPT)
        
        # Create Gemini model
        model = genai.GenerativeModel('gemini-pro')
        
        # Build conversation context
        conversation_context = []
        for msg in conversation_history[session_id]:
            conversation_context.append(f"{msg['role']}: {msg['content']}")
        
        # Add system prompt and current message
        full_prompt = f"{system_prompt}\n\n"
        if conversation_context:
            full_prompt += "Previous conversation:\n" + "\n".join(conversation_context) + "\n\n"
        full_prompt += f"User: {chat_message.message}\nAssistant:"
        
        # Generate response from Gemini
        response = model.generate_content(full_prompt)
        bot_response = response.text
        
        # Store conversation history
        conversation_history[session_id].append({
            "role": "User",
            "content": chat_message.message,
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation_history[session_id].append({
            "role": "Assistant",
            "content": bot_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return ChatResponse(
            response=bot_response,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )


@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get conversation history for a specific session.
    """
    if session_id not in conversation_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No conversation history found for session: {session_id}"
        )
    
    return {
        "session_id": session_id,
        "history": conversation_history[session_id],
        "message_count": len(conversation_history[session_id])
    }


@app.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear conversation history for a specific session.
    """
    if session_id not in conversation_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No conversation history found for session: {session_id}"
        )
    
    del conversation_history[session_id]
    
    return {
        "message": "Conversation history cleared",
        "session_id": session_id
    }


@app.post("/admin/system-prompt", response_model=SystemPromptResponse)
async def update_system_prompt(prompt_update: SystemPromptUpdate):
    """
    Update the system prompt for the chatbot.
    
    This allows customizing the chatbot's behavior and service profile.
    You can create different profiles for different service types.
    """
    profile_name = prompt_update.profile_name or "default"
    custom_prompts[profile_name] = prompt_update.prompt
    
    return SystemPromptResponse(
        message=f"System prompt updated successfully for profile: {profile_name}",
        profile_name=profile_name,
        prompt=prompt_update.prompt
    )


@app.get("/admin/system-prompt/{profile_name}")
async def get_system_prompt(profile_name: str = "default"):
    """
    Get the current system prompt for a specific profile.
    """
    prompt = custom_prompts.get(profile_name, DEFAULT_SYSTEM_PROMPT if profile_name == "default" else None)
    
    if prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No system prompt found for profile: {profile_name}"
        )
    
    return {
        "profile_name": profile_name,
        "prompt": prompt
    }


@app.get("/admin/profiles")
async def list_profiles():
    """
    List all available service profiles.
    """
    profiles = list(custom_prompts.keys())
    if "default" not in profiles:
        profiles.insert(0, "default")
    
    return {
        "profiles": profiles,
        "count": len(profiles)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
