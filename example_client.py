#!/usr/bin/env python3
"""
Example client for the Customer Service Chatbot API

This script demonstrates how to interact with the chatbot API.
"""

import requests
import json
from typing import Optional

# API Configuration
API_BASE_URL = "http://localhost:8000"


def check_health():
    """Check if the API is healthy"""
    response = requests.get(f"{API_BASE_URL}/health")
    return response.json()


def send_message(message: str, session_id: Optional[str] = None):
    """Send a message to the chatbot"""
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json=payload
    )
    return response.json()


def get_history(session_id: str):
    """Get conversation history for a session"""
    response = requests.get(f"{API_BASE_URL}/chat/history/{session_id}")
    return response.json()


def clear_history(session_id: str):
    """Clear conversation history for a session"""
    response = requests.delete(f"{API_BASE_URL}/chat/history/{session_id}")
    return response.json()


def update_system_prompt(prompt: str, profile_name: str = "default"):
    """Update the system prompt"""
    payload = {
        "prompt": prompt,
        "profile_name": profile_name
    }
    response = requests.post(
        f"{API_BASE_URL}/admin/system-prompt",
        json=payload
    )
    return response.json()


def get_system_prompt(profile_name: str = "default"):
    """Get the current system prompt"""
    response = requests.get(f"{API_BASE_URL}/admin/system-prompt/{profile_name}")
    return response.json()


def list_profiles():
    """List all available service profiles"""
    response = requests.get(f"{API_BASE_URL}/admin/profiles")
    return response.json()


def main():
    """Main example demonstrating API usage"""
    print("=" * 60)
    print("Customer Service Chatbot API - Example Client")
    print("=" * 60)
    print()
    
    # Check health
    print("1. Checking API health...")
    health = check_health()
    print(f"   Status: {health['status']}")
    print(f"   Gemini configured: {health['gemini_configured']}")
    print()
    
    # Start a conversation
    print("2. Starting a conversation...")
    response1 = send_message("What cleaning services do you offer?")
    session_id = response1['session_id']
    print(f"   Session ID: {session_id}")
    print(f"   Bot: {response1['response']}")
    print()
    
    # Continue the conversation
    print("3. Continuing the conversation...")
    response2 = send_message(
        "How much does deep cleaning cost?",
        session_id=session_id
    )
    print(f"   Bot: {response2['response']}")
    print()
    
    # Get conversation history
    print("4. Getting conversation history...")
    history = get_history(session_id)
    print(f"   Total messages: {history['message_count']}")
    for msg in history['history']:
        print(f"   {msg['role']}: {msg['content'][:50]}...")
    print()
    
    # List profiles
    print("5. Listing service profiles...")
    profiles = list_profiles()
    print(f"   Available profiles: {', '.join(profiles['profiles'])}")
    print()
    
    # Create a custom profile (optional)
    print("6. Creating a custom service profile...")
    custom_prompt = """You are a customer service agent for TechFix IT Services.
    Help customers with computer repairs, network setup, and tech support.
    Be technical but friendly."""
    
    update_result = update_system_prompt(custom_prompt, "tech-support")
    print(f"   {update_result['message']}")
    print()
    
    # Clear history
    print("7. Clearing conversation history...")
    clear_result = clear_history(session_id)
    print(f"   {clear_result['message']}")
    print()
    
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Please make sure the server is running at", API_BASE_URL)
    except Exception as e:
        print(f"Error: {e}")
