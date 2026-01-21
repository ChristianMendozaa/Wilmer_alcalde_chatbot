from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat_models import ChatRequest
from app.agent.wilmer_agent import get_agent
import json
import asyncio
from typing import AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter()


async def generate_chat_stream(message: str, conversation_history: list) -> AsyncGenerator[str, None]:
    """
    Generate streaming chat response compatible with Vercel AI SDK.
    
    Uses the Vercel AI SDK Data Stream Protocol format:
    - Text chunks: 0:"token"
    - Finish: d:{"finishReason":"stop"}
    
    Args:
        message: User's message
        conversation_history: Previous conversation messages
        
    Yields:
        Vercel AI SDK formatted stream chunks
    """
    try:
        agent = get_agent()

        # Format conversation history for the agent
        chat_history = []
        for msg in conversation_history:
            role = msg.role
            content = msg.content
            if role == "user":
                chat_history.append(HumanMessage(content=content))
            elif role == "assistant":
                chat_history.append(AIMessage(content=content))
        
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
        
        # Stream the response token by token using Vercel AI SDK format
        # Format: 0:"token" (0 = text type)
        words = output.split()
        
        for i, word in enumerate(words):
            # Add space before word except for the first one
            token = word if i == 0 else f" {word}"
            
            # Vercel AI SDK Data Stream Protocol: 0:"text_content"
            yield f'0:{json.dumps(token)}\n'
            
            # Small delay to simulate streaming
            await asyncio.sleep(0.02)
        
        # Send finish event: d:{"finishReason":"stop"}
        yield f'd:{json.dumps({"finishReason": "stop"})}\n'
        
    except Exception as e:
        # Send error event: 3:"error message"
        yield f'3:{json.dumps(str(e))}\n'


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
