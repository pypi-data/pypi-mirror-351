# LangChain Core Utilities

A production-grade Python package for LangChain operations with token tracking, RAG, and agent support.

## Features

- 🤖 Advanced Agent implementations with tool support
- 📚 RAG (Retrieval Augmented Generation) with configurable vector stores
- 💬 Chat functionality with memory and history
- 📊 Token usage tracking and cost monitoring
- 🔄 Both sync and async execution
- 🎯 Configurable via environment variables or code
- 📝 MongoDB or file-based logging
- 🔤 Flexible embedding service with multiple providers

## Installation

```bash
# Using Poetry
poetry add abs-langchain-core

# Using pip
pip install abs-langchain-core
```

## Quick Start

### Basic Configuration

```python
from abs_langchain_core import Config, UsageLogger

# Load configuration from environment variables
config = Config.from_env()

# Initialize logger
logger = UsageLogger(
    log_to_file=True,
    log_to_mongo=True,
    mongo_uri="mongodb://localhost:27017",
)
```

### Embedding Usage

```python
from abs_langchain_core import EmbeddingService

# Create embedding service with OpenAI provider
embedding_service = EmbeddingService(
    provider="openai",
    model_name="text-embedding-3-small",
    logger=logger,
)

# Embed a single text
embedding = embedding_service.embed_query("Hello, world!")

# Embed multiple documents
documents = ["Document 1 content", "Document 2 content"]
result = embedding_service.embed_documents(
    texts=documents,
    batch_size=100
)

# Get embedding metadata
metadata = embedding_service.get_metadata()
print(f"Model: {metadata.model_name}")
print(f"Dimensions: {metadata.dimensions}")
```

### Async Embedding

```python
import asyncio

async def process_documents():
    service = EmbeddingService(provider="openai")
    
    # Async single query
    embedding = await service.aembed_query("Hello, world!")
    
    # Async batch processing
    result = await service.aembed_documents(
        texts=["Document 1", "Document 2"],
        batch_size=50
    )
    return result
```

### CLI Usage

```bash
# Basic usage
python -m abs_langchain_core.cli.embed_documents input.json output.json

# With custom provider and model
python -m abs_langchain_core.cli.embed_documents \
    input.json output.json \
    --provider openai \
    --model-name text-embedding-3-small \
    --batch-size 50
```

### Chat Usage

```python
from abs_langchain_core import ChatService
from langchain.memory import ConversationBufferMemory

# Create chat service
chat_service = ChatService(
    model_name="gpt-4",
    temperature=0.7,
    logger=logger,
    memory=ConversationBufferMemory(),
)

# Send a message
response = chat_service.chat("What is the capital of France?")

# Get chat history
history = chat_service.get_chat_history()
```

### RAG Implementation

```python
from abs_langchain_core import RAGService
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Create vector store
vector_store = Chroma(
    embedding_function=OpenAIEmbeddings(),
    persist_directory="./data/chroma",
)

# Create RAG service
rag_service = RAGService(
    vector_store=vector_store,
    model_name="gpt-4",
    temperature=0.7,
    logger=logger,
)

# Add documents
documents = ["Document 1 content", "Document 2 content"]
rag_service.add_documents(documents)

# Query documents
response = rag_service.query("What are the key points in the documents?")
```

### Agent Usage

```python
from abs_langchain_core import AgentService
from langchain.tools import Tool

# Create tools
tools = [
    Tool(
        name="search",
        func=lambda x: "Search results for: " + x,
        description="Search for information",
    ),
]

# Create agent service
agent_service = AgentService(
    tools=tools,
    model_name="gpt-4",
    temperature=0.7,
    logger=logger,
)

# Run agent
response = agent_service.run("Search for information about Python")
```

### Async Usage

All services support async operations:

```python
import asyncio

# Async chat
response = await chat_service.achat("What is the weather?")

# Async RAG
response = await rag_service.aquery("What are the key points?")

# Async agent
response = await agent_service.arun("Search for information")
```

### Token Usage Tracking

```python
from abs_langchain_core import UsageLogger

# Initialize logger
logger = UsageLogger(
    log_to_file=True,
    log_to_mongo=True,
    mongo_uri="mongodb://localhost:27017",
)

# Get usage statistics
stats = logger.get_usage_stats(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    model_name="gpt-4",
)

print(f"Total tokens: {stats['total_tokens']}")
print(f"Total cost: ${stats['total_cost']:.2f}")
```

## Configuration

The package can be configured using environment variables:

```env
# Model configuration
LLM_MODEL_NAME=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
LLM_TOP_P=1.0
LLM_FREQUENCY_PENALTY=0.0
LLM_PRESENCE_PENALTY=0.0

# Logging configuration
LOG_TO_FILE=true
LOG_TO_MONGO=true
LOG_DIR=logs
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=langchain_usage
MONGODB_COLLECTION=usage_logs

# RAG configuration
EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
VECTOR_STORE_TYPE=chroma

# Agent configuration
AGENT_MAX_ITERATIONS=5
AGENT_RETURN_INTERMEDIATE_STEPS=false
AGENT_VERBOSE=true

# Embedding configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL_NAME=text-embedding-3-small
EMBEDDING_BATCH_SIZE=100
```

## Development

```bash
# Install dependencies
poetry install

# Format code
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 