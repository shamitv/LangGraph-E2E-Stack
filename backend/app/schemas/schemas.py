"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str = Field(..., description="Message content")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    agent_type: Optional[str] = Field("default", description="Type of agent to use")


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID")
    agent_type: str = Field(..., description="Agent type used")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: int
    session_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConversationHistoryResponse(BaseModel):
    """Schema for conversation history."""
    conversation: ConversationResponse
    messages: List[MessageResponse]
