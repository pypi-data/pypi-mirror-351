from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Model for tracking token usage in LLM calls."""
    prompt_tokens: int = Field(default=0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(default=0, description="Number of tokens in the completion")
    total_tokens: int = Field(default=0, description="Total number of tokens used")
    cost_usd: float = Field(default=0.0, description="Cost in USD")
    model_name: str = Field(..., description="Name of the model used")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the usage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for tracking")


class UsageLog(BaseModel):
    """Model for storing usage logs in the database."""
    user_id: Optional[str] = Field(None, description="ID of the user making the request")
    request_id: str = Field(..., description="Unique identifier for the request")
    usage: TokenUsage = Field(..., description="Token usage details")
    operation_type: str = Field(..., description="Type of operation (chat, rag, agent)")
    status: str = Field(default="success", description="Status of the operation")
    error_message: Optional[str] = Field(None, description="Error message if any")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of creation")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last update") 