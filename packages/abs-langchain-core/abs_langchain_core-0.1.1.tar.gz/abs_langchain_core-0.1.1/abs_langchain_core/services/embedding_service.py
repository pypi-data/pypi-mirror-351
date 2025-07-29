from typing import List, Optional, Dict, Any, Union
from ..interfaces.embedding_provider import EmbeddingProvider
from ..core.logger import UsageLogger
from ..providers.openai_provider import OpenAIEmbeddingProvider
from ..schemas.embedding_response_schema import EmbeddingResponse
from ..schemas.embedding_metadata_schema import EmbeddingMetadata
from abs_exception_core.exceptions import GenericHttpError

class EmbeddingService:
    """Service for handling text embeddings with multiple providers."""

    def __init__(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        logger: Optional[UsageLogger] = None,
        **kwargs
    ):
        """Initialize the embedding service.
        
        Args:
            provider: Name of the embedding provider to use ('openai' or 'huggingface')
            model_name: Optional model name to override default
            logger: Optional usage logger
            **kwargs: Additional arguments to pass to the provider
            
        Raises:
            GenericHttpError: If initialization fails
        """
        try:
            self.provider = self._get_provider(provider, model_name, logger, **kwargs)
            self.logger = logger
        except Exception as e:
            raise GenericHttpError(f"Failed to initialize embedding service: {str(e)}")

    def _get_provider(
        self,
        provider: str,
        model_name: Optional[str],
        logger: Optional[UsageLogger],
        **kwargs
    ) -> EmbeddingProvider:
        """Get the appropriate embedding provider.
        
        Args:
            provider: Name of the provider
            model_name: Optional model name
            logger: Optional logger
            **kwargs: Additional provider arguments
            
        Returns:
            Configured embedding provider
            
        Raises:
            GenericHttpError: If provider initialization fails
        """
        try:
            if provider.lower() == "openai":
                return OpenAIEmbeddingProvider(
                    model_name=model_name or "text-embedding-3-small",
                    logger=logger,
                    **kwargs
                )
            else:
                raise ValueError(f"Unsupported embedding provider: {provider}")
        except Exception as e:
            raise GenericHttpError(f"Failed to initialize provider: {str(e)}")

    def embed_documents(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> EmbeddingResponse:
        """Embed a list of documents.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            EmbeddingResponse with results
            
        Raises:
            GenericHttpError: If embedding fails
        """
        try:
            # Process in batches
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = self.provider.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)

            return EmbeddingResponse(
                embeddings=all_embeddings,
                model_name=self.provider.model_name,
                dimensions=self.provider.embedding_dimensions
            )
        except Exception as e:
            raise GenericHttpError(f"Failed to embed documents: {str(e)}")

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as a list of floats
            
        Raises:
            GenericHttpError: If embedding fails
        """
        try:
            return self.provider.embed_query(text)
        except Exception as e:
            raise GenericHttpError(f"Failed to embed query: {str(e)}")

    async def aembed_documents(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> EmbeddingResponse:
        """Asynchronously embed a list of documents.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            EmbeddingResponse with results
            
        Raises:
            GenericHttpError: If embedding fails
        """
        try:
            # Process in batches
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = await self.provider.aembed_documents(batch)
                all_embeddings.extend(batch_embeddings)

            return EmbeddingResponse(
                embeddings=all_embeddings,
                model_name=self.provider.model_name,
                dimensions=self.provider.embedding_dimensions
            )
        except Exception as e:
            raise GenericHttpError(f"Failed to embed documents asynchronously: {str(e)}")

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronously embed a single query text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding as a list of floats
            
        Raises:
            GenericHttpError: If embedding fails
        """
        try:
            return await self.provider.aembed_query(text)
        except Exception as e:
            raise GenericHttpError(f"Failed to embed query asynchronously: {str(e)}")

    def get_metadata(self) -> EmbeddingMetadata:
        """Get metadata about the embedding service.
        
        Returns:
            EmbeddingMetadata with service configuration
        """
        return EmbeddingMetadata(
            model_name=self.provider.model_name,
            dimensions=self.provider.embedding_dimensions,
            provider=self.provider.__class__.__name__
        ) 