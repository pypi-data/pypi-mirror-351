from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class EmbeddingResponse(BaseModel):
    """Schema for embedding response."""
    model_config = ConfigDict(extra='forbid')
    
    embeddings: List[List[float]] = Field(
        ...,
        description="List of embeddings"
    )
    model_name: str = Field(
        ...,
        description="Name of the model used"
    )
    dimensions: int = Field(
        ...,
        description="Number of dimensions in the embeddings",
        gt=0
    )
    cached: bool = Field(default=False, description="Whether the result was from cache")