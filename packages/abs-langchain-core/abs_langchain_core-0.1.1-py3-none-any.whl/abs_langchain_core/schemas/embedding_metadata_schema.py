from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class EmbeddingMetadata(BaseModel):
    """Schema for embedding metadata."""
    model_config = ConfigDict(extra='forbid')
    
    model_name: str = Field(
        ...,
        description="Name of the model used"
    )
    dimensions: int = Field(
        ...,
        description="Number of dimensions in the embeddings",
        gt=0
    )
    provider: str = Field(
        ...,
        description="Name of the embedding provider"
    )
    batch_size: Optional[int] = Field(
        default=None,
        description="Batch size used",
        gt=0
    )
    cache_enabled: bool = Field(default=False, description="Whether caching is enabled") 