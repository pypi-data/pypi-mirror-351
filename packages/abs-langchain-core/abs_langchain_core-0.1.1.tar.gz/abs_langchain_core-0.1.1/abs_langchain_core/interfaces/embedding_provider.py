from abc import ABC, abstractmethod
from typing import List, Protocol, runtime_checkable

@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol defining the interface for embedding providers.
    
    This protocol ensures that all embedding providers implement the required methods
    for both synchronous and asynchronous embedding operations.
    """
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings, where each embedding is a list of floats
            
        Raises:
            EmbeddingError: If embedding fails
        """
        ...
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as a list of floats
            
        Raises:
            EmbeddingError: If embedding fails
        """
        ...
    
    @abstractmethod
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously embed a list of documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings, where each embedding is a list of floats
            
        Raises:
            EmbeddingError: If embedding fails
        """
        ...
    
    @abstractmethod
    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronously embed a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as a list of floats
            
        Raises:
            EmbeddingError: If embedding fails
        """
        ...
    
    @property
    @abstractmethod
    def embedding_dimensions(self) -> int:
        """Get the dimensions of the embeddings.
        
        Returns:
            Number of dimensions in the embedding vectors
        """
        ...
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the name of the embedding model.
        
        Returns:
            Name of the model being used
        """
        ... 