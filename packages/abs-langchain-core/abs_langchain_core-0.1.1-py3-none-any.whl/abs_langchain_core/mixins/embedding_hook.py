from typing import TypeVar, Type, Optional, Dict, Any, List, Generic
from pydantic import BaseModel
from ..services.embedding_service import EmbeddingService
from ..schemas.embedding_config_schema import EmbeddingConfig
from ..schemas.cosmo_vector_config_schema import CosmosVectorConfig
from ..core.logger import UsageLogger
from abs_exception_core.exceptions import (
    GenericHttpError,
    NotFoundError
)
import asyncio

T = TypeVar('T', bound=BaseModel)


class EmbeddingHookMixin(Generic[T]):
    """Mixin to add embedding capabilities to services.
    
    This mixin provides methods to handle embedding generation and storage
    for CRUD operations on models that need vector embeddings.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        embedding_config: EmbeddingConfig,
        cosmos_config: CosmosVectorConfig,
        logger: Optional[UsageLogger] = None
    ):
        """Initialize the embedding hook mixin.
        
        Args:
            embedding_service: Configured embedding service
            embedding_config: Configuration for each model type
            cosmos_config: Cosmos DB configuration
            logger: Optional usage logger
        """
        self.embedding_service = embedding_service
        self.embedding_config = embedding_config
        self.cosmos_config = cosmos_config
        self.logger = logger
        # Get the container using the proper Cosmos DB client method
        self.database = cosmos_config.database
        self._container = self.database.get_container_client(cosmos_config.container_name)

    async def embed_on_create(
        self,
        record_id: str,
        text: str,
        record: T
    ) -> None:
        """Generate and store embedding for a new record if enabled.
        
        Args:
            record: The record to embed
            model_type: Type of the record
            
        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            # Generate embedding
            embedding = await self.embedding_service.aembed_query(text)

            # Convert record to dict if it's a Pydantic model
            record_dict = record.model_dump() if hasattr(record, 'model_dump') else record

            # Store in Cosmos DB
            vector_doc = {
                "id": str(record_id),  # Cosmos DB uses 'id'
                self.cosmos_config.vector_field: embedding,
                **record_dict
            }
            self._container.create_item(body=vector_doc)

        except Exception as e:
            raise GenericHttpError(f"Failed to embed on create: {str(e)}")

    async def embed_on_update(
        self,
        record_id: str,
        record: T,
        text: str
    ) -> None:
        """Update embedding if the target field has changed.
        
        Args:
            record_id: ID of the record
            record: Updated record
            text: Text to embed
            
        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            # Get the Document from the Cosmos DB
            document = self._container.read_item(item=str(record_id), partition_key=str(record_id))
            if not document:
                raise NotFoundError(f"Document not found for record_id: {record_id}")

            # Generate the embedding
            embedding = await self.embedding_service.aembed_query(text)

            # Convert record to dict if it's a Pydantic model
            record_dict = record.model_dump() if hasattr(record, 'model_dump') else record

            # Update in Cosmos DB
            vector_doc = {
                "id": str(record_id),
                self.cosmos_config.vector_field: embedding,
                **record_dict
            }
            self._container.upsert_item(body=vector_doc)

        except Exception as e:
            raise GenericHttpError(f"Failed to embed on update: {str(e)}")

    async def delete_vector(
        self,
        record_id: str
    ) -> None:
        """Delete vector embedding if enabled.
        
        Args:
            record_id: ID of the record
            model_type: Type of the record
            
        Raises:
            EmbeddingError: If deletion fails
        """
        try:
            self._container.delete_item(item=str(record_id), partition_key=str(record_id))
        except Exception as e:
            raise GenericHttpError(f"Failed to delete vector: {str(e)}")

    async def bulk_delete_vector(self, records: list[dict]):
        try:
            tasks = [
                self._container.delete_item(item=rec['id'], partition_key=rec['partition_key'])
                for rec in records
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            raise GenericHttpError(f"Parallel bulk deletion failed: {e}")


    async def search_similar(
        self,
        query_text: str,
        limit: int = 10,
        projection_fields: list[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar records using vector similarity.
        
        Args:
            query_text: Text to search for
            model_type: Type of records to search
            limit: Maximum number of results
            min_score: Minimum similarity score
            
        Returns:
            List of similar records with scores
            
        Raises:
            EmbeddingError: If search fails
        """
        #TODO: NEED TO IMPROVE
        try:
            # Generate query embedding
            query_vector = await self.embedding_service.aembed_query(query_text)
            fields_str = ""
            if projection_fields:
                fields_str = ", ".join([f"c.{field}" for field in projection_fields])
            else:
                fields_str = "*"


            # Perform vector search using Cosmos DB's vector search
            query = f""" SELECT TOP {limit} {fields_str}, VectorDistance(c.{self.cosmos_config.vector_field}, {query_vector}) as score FROM c  ORDER BY VectorDistance(c.{self.cosmos_config.vector_field}, {query_vector})"""
            results = list(self._container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))

            return results

        except Exception as e:
            raise GenericHttpError(f"Failed to search similar: {str(e)}") 