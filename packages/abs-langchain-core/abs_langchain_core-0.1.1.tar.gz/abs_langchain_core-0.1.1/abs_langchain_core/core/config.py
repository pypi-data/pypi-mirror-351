from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ModelConfig(BaseModel):
    """Configuration for LLM models."""

    model_name: str = Field(default="gpt-3.5-turbo", description="Name of the model to use")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(default=None, description="Top-p sampling parameter")
    frequency_penalty: Optional[float] = Field(default=None, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(default=None, description="Presence penalty")


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    log_to_file: bool = Field(default=True, description="Whether to log to file")
    log_to_mongo: bool = Field(default=False, description="Whether to log to MongoDB")
    log_dir: Optional[str] = Field(default="logs", description="Directory to store log files")
    mongo_uri: Optional[str] = Field(default=None, description="MongoDB connection URI")
    mongo_db: str = Field(default="langchain_usage", description="MongoDB database name")
    mongo_collection: str = Field(default="usage_logs", description="MongoDB collection name")


class RAGConfig(BaseModel):
    """Configuration for RAG operations."""

    embedding_model: str = Field(default="text-embedding-ada-002", description="Name of the embedding model")
    chunk_size: int = Field(default=1000, description="Size of text chunks for splitting")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")
    vector_store_type: str = Field(default="chroma", description="Type of vector store to use")
    vector_store_config: Dict[str, Any] = Field(default_factory=dict, description="Vector store configuration")


class AgentConfig(BaseModel):
    """Configuration for agent operations."""

    max_iterations: int = Field(default=5, description="Maximum number of iterations")
    return_intermediate_steps: bool = Field(default=False, description="Whether to return intermediate steps")
    verbose: bool = Field(default=True, description="Whether to print verbose output")


class Config(BaseModel):
    """Main configuration class."""

    model: ModelConfig = Field(default_factory=ModelConfig, description="Model configuration")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    rag: RAGConfig = Field(default_factory=RAGConfig, description="RAG configuration")
    agent: AgentConfig = Field(default_factory=AgentConfig, description="Agent configuration")

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables.

        Returns:
            Config: Configuration instance
        """
        return cls(
            model=ModelConfig(
                model_name=os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "0")) or None,
                top_p=float(os.getenv("LLM_TOP_P", "0")) or None,
                frequency_penalty=float(os.getenv("LLM_FREQUENCY_PENALTY", "0")) or None,
                presence_penalty=float(os.getenv("LLM_PRESENCE_PENALTY", "0")) or None,
            ),
            logging=LoggingConfig(
                log_to_file=os.getenv("LOG_TO_FILE", "true").lower() == "true",
                log_to_mongo=os.getenv("LOG_TO_MONGO", "false").lower() == "true",
                log_dir=os.getenv("LOG_DIR", "logs"),
                mongo_uri=os.getenv("MONGODB_URI"),
                mongo_db=os.getenv("MONGODB_DB", "langchain_usage"),
                mongo_collection=os.getenv("MONGODB_COLLECTION", "usage_logs"),
            ),
            rag=RAGConfig(
                embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"),
                chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
                chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
                vector_store_type=os.getenv("VECTOR_STORE_TYPE", "chroma"),
                vector_store_config={},  # TODO: Parse from env
            ),
            agent=AgentConfig(
                max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "5")),
                return_intermediate_steps=os.getenv("AGENT_RETURN_INTERMEDIATE_STEPS", "false").lower() == "true",
                verbose=os.getenv("AGENT_VERBOSE", "true").lower() == "true",
            ),
        ) 