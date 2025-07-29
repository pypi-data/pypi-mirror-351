
from pydantic import BaseModel

class EmbeddingConfig(BaseModel):
    """Configuration for embedding a specific model type."""
    provider: str = "openai"
