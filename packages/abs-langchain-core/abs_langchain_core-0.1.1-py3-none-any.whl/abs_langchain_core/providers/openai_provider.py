from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from ..interfaces.embedding_provider import EmbeddingProvider
from ..core.logger import UsageLogger
from abs_exception_core.exceptions import GenericHttpError

class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider implementation."""

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        logger: Optional[UsageLogger] = None,
        **kwargs
    ):
        """Initialize the OpenAI embedding provider.
        
        Args:
            model_name: Name of the OpenAI embedding model to use
            logger: Optional usage logger
            **kwargs: Additional arguments to pass to OpenAIEmbeddings
            
        Raises:
            EmbeddingError: If initialization fails
        """
        try:
            self._model_name = model_name
            self.logger = logger
            self._embeddings = OpenAIEmbeddings(
                model=model_name,
                **kwargs
            )
        except Exception as e:
            raise GenericHttpError(f"Failed to initialize OpenAI provider: {str(e)}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using OpenAI.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
            
        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            if self.logger:
                self.logger.log_embedding_usage(
                    model_name=self.model_name,
                    num_tokens=sum(len(text.split()) for text in texts)
                )
            return self._embeddings.embed_documents(texts)
        except Exception as e:
            raise GenericHttpError(f"Failed to embed documents: {str(e)}")

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as a list of floats
            
        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            if self.logger:
                self.logger.log_embedding_usage(
                    model_name=self.model_name,
                    num_tokens=len(text.split())
                )
            return self._embeddings.embed_query(text)
        except Exception as e:
            raise GenericHttpError(f"Failed to embed query: {str(e)}")

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously embed a list of documents using OpenAI.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
            
        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            if self.logger:
                self.logger.log_embedding_usage(
                    model_name=self.model_name,
                    num_tokens=sum(len(text.split()) for text in texts)
                )
            return await self._embeddings.aembed_documents(texts)
        except Exception as e:
            raise GenericHttpError(f"Failed to embed documents asynchronously: {str(e)}")

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronously embed a single query text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as a list of floats
            
        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            if self.logger:
                self.logger.log_embedding_usage(
                    model_name=self.model_name,
                    num_tokens=len(text.split())
                )
            return await self._embeddings.aembed_query(text)
        except Exception as e:
            raise GenericHttpError(f"Failed to embed query asynchronously: {str(e)}")

    @property
    def embedding_dimensions(self) -> int:
        """Get the dimensions of the OpenAI embeddings.
        
        Returns:
            Number of dimensions in the embedding vectors
        """
        # OpenAI's text-embedding-3-small has 1536 dimensions
        # text-embedding-3-large has 3072 dimensions
        return 1536 if "small" in self.model_name else 3072

    @property
    def model_name(self) -> str:
        """Get the name of the embedding model.
        
        Returns:
            Name of the model being used
        """
        return self._model_name 