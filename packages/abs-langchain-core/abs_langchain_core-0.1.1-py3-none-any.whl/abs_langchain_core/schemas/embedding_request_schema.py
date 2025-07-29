from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class EmbeddingRequest(BaseModel):
    """Schema for embedding request."""
    model_config = ConfigDict(extra='forbid')
    
    texts: List[str] = Field(
        ...,
        description="List of texts to embed",
        min_items=1
    )
    batch_size: Optional[int] = Field(
        default=100,
        description="Batch size for processing",
        gt=0
    )
    cache_key: Optional[str] = Field(default=None, description="Optional cache key for the request")
