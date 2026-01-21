from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ChatMessage(BaseModel):
    """Represents a single message in a conversation."""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation messages"
    )


class ChatResponse(BaseModel):
    """Response model for synchronous chat endpoint."""
    output: str = Field(..., description="Agent's response")


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    success: bool
    message: str
    chunks_created: int
    filename: str

