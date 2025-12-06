"""
Agent API endpoints for GPT-4o-mini integration.
"""
import os
import uuid
from typing import Dict, List
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from models import AgentRequest, AgentResponse

# Load environment variables from .env file
load_dotenv()

router = APIRouter(prefix="/api/agent", tags=["agent"])


def get_openai_client() -> OpenAI:
    """
    Get OpenAI client instance with API key from environment.
    
    Returns:
        OpenAI client instance
        
    Raises:
        HTTPException: If OPEN_AI_API_KEY is not found in environment variables
    """
    api_key = os.getenv("OPEN_AI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPEN_AI_API_KEY not found in environment variables. Please check your .env file."
        )
    return OpenAI(api_key=api_key)

# In-memory storage for conversation threads
# Format: {thread_id: [{"role": "user"|"assistant", "content": "..."}, ...]}
conversation_threads: Dict[str, List[Dict[str, str]]] = {}


def get_or_create_thread(thread_id: str) -> List[Dict[str, str]]:
    """
    Get conversation history for a thread, or create a new thread if it doesn't exist.
    
    Args:
        thread_id: Thread identifier
        
    Returns:
        List of conversation messages
    """
    if thread_id not in conversation_threads:
        conversation_threads[thread_id] = []
    return conversation_threads[thread_id]


def generate_thread_id() -> str:
    """Generate a new unique thread ID."""
    return f"thread_{uuid.uuid4().hex[:12]}"


@router.post("/chat", response_model=AgentResponse)
async def agent_chat(request: AgentRequest):
    """
    Chat with GPT-4o-mini agent with conversation memory.
    
    This endpoint takes a user prompt and returns a response from GPT-4o-mini.
    If a thread_id is provided, the conversation continues from that thread's history.
    If no thread_id is provided, a new conversation thread is created.
    
    Args:
        request: Agent chat request with prompt and optional thread_id
        
    Returns:
        Agent response with the AI's reply and thread_id for continuing the conversation
        
    Example curl request:
    ```bash
    curl -X POST http://localhost:8000/api/agent/chat \
      -H "Content-Type: application/json" \
      -d '{
        "prompt": "Hello, what can you help me with?",
        "thread_id": "thread_abc123"
      }'
    ```
    """
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # Get or create thread
        thread_id = request.thread_id or generate_thread_id()
        conversation_history = get_or_create_thread(thread_id)
        
        # Add user message to conversation history
        conversation_history.append({
            "role": "user",
            "content": request.prompt
        })
        
        # Call OpenAI API with conversation history
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract assistant's response
        assistant_message = response.choices[0].message.content
        
        # Add assistant's response to conversation history
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return AgentResponse(
            response=assistant_message,
            thread_id=thread_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with OpenAI API: {str(e)}"
        )

