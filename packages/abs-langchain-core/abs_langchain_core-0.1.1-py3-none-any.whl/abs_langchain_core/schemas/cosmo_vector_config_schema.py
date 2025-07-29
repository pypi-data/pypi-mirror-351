from pydantic import BaseModel, ConfigDict
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Any
class CosmosVectorConfig(BaseModel):
    """Configuration for Cosmos DB vector storage."""
  
    database: Any
    container_name: str
    vector_field: str = "vector"
