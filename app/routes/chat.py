from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat_models import ChatRequest
from app.agent.wilmer_agent import get_agent
import json
import asyncio
from typing import AsyncGenerator


router = APIRouter()


async def generate_chat_stream(message: str, conversation_history: list) -> AsyncGenerator[str, None]:
    """
    Generate streaming chat response compatible with Vercel AI SDK.
    
    Args:
        message: User's message
        conversation_history: Previous conversation messages
        
    Yields:
        Server-Sent Events formatted strings
    """
    try:
        agent = get_agent()
        
        # Format conversation history for the agent
        chat_history = ""
        for msg in conversation_history:
            role = msg.role
            content = msg.content
            if role == "user":
                chat_history += f"Usuario: {content}\n"
            elif role == "assistant":
                chat_history += f"Dr. Wilmer Gálvez: {content}\n"
        
        # Prepare input for the agent
        agent_input = {
            "input": message,
            "chat_history": chat_history
        }
        
        # Run agent in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def run_agent():
            return agent.invoke(agent_input)
        
        result = await loop.run_in_executor(None, run_agent)
        
        # Extract the final output
        output = result.get("output", "")
        
        # Stream the response token by token
        # Simulate token-by-token streaming by splitting into words
        words = output.split()
        
        for i, word in enumerate(words):
            # Add space before word except for the first one
            token = word if i == 0 else f" {word}"
            
            # Format as Vercel AI SDK compatible event
            event_data = {
                "type": "text",
                "content": token
            }
            
            yield f"data: {json.dumps(event_data)}\n\n"
            
            # Small delay to simulate streaming
            await asyncio.sleep(0.01)
        
        # Send completion event
        done_event = {"type": "done"}
        yield f"data: {json.dumps(done_event)}\n\n"
        
    except Exception as e:
        # Send error event
        error_event = {
            "type": "error",
            "error": str(e)
        }
        yield f"data: {json.dumps(error_event)}\n\n"


@router.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint with streaming support compatible with Vercel AI SDK.
    
    This endpoint:
    1. Receives a user message and conversation history
    2. Executes the Dr. Wilmer Gálvez agent
    3. Streams the response token by token
    
    Args:
        request: ChatRequest with message and conversation history
        
    Returns:
        StreamingResponse with Server-Sent Events
    """
    
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="El mensaje no puede estar vacío"
        )
    
    return StreamingResponse(
        generate_chat_stream(request.message, request.conversation_history),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )
