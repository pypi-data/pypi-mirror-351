from typing import Optional, List, Dict, Any
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from .base import BaseService
from ..core.logger import UsageLogger

#TODO: THIS IS NOT COMPLETE
class RAGService(BaseService):
    """Service for Retrieval-Augmented Generation (RAG) operations."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: Optional[Embeddings] = None,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        logger: Optional[UsageLogger] = None,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize the RAG service.

        Args:
            vector_store: Vector store for document retrieval
            embedding_model: Optional embedding model for document indexing
            model_name: Name of the model to use
            temperature: Temperature for generation
            logger: Optional usage logger
            system_prompt: Optional system prompt to use
            **kwargs: Additional arguments to pass to the model
        """
        super().__init__(
            model_name=model_name,
            temperature=temperature,
            logger=logger,
            system_prompt=system_prompt or "You are a helpful AI assistant that answers questions based on the provided context.",
            **kwargs,
        )
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def add_documents(
        self,
        documents: List[Document],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add documents to the vector store.

        Args:
            documents: List of documents to add
            metadata: Optional metadata to add to the documents
        """
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)

        self.vector_store.add_documents(documents)

    def create_rag_chain(
        self,
        prompt_template: Optional[str] = None,
        retriever: Optional[BaseRetriever] = None,
    ):
        """Create a RAG chain.

        Args:
            prompt_template: Optional prompt template to use
            retriever: Optional retriever to use

        Returns:
            Chain: Configured RAG chain
        """
        # Use default retriever if none provided
        retriever = retriever or self.vector_store.as_retriever()

        # Create prompt template
        if prompt_template:
            prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "Context: {context}\n\nQuestion: {question}")
            ])

        # Create chain
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm_provider.get_chat_model()
            | StrOutputParser()
        )

        return chain

    async def acreate_rag_chain(
        self,
        prompt_template: Optional[str] = None,
        retriever: Optional[BaseRetriever] = None,
    ):
        """Create an async RAG chain.

        Args:
            prompt_template: Optional prompt template to use
            retriever: Optional retriever to use

        Returns:
            Chain: Configured async RAG chain
        """
        # Use default retriever if none provided
        retriever = retriever or self.vector_store.as_retriever()

        # Create prompt template
        if prompt_template:
            prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "Context: {context}\n\nQuestion: {question}")
            ])

        # Get the chat model asynchronously
        chat_model = await self.llm_provider.aget_chat_model()

        # Create chain
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | chat_model
            | StrOutputParser()
        )

        return chain

    def query(
        self,
        question: str,
        prompt_template: Optional[str] = None,
        retriever: Optional[BaseRetriever] = None,
        **kwargs: Any,
    ) -> str:
        """Query the RAG system.

        Args:
            question: Question to ask
            prompt_template: Optional prompt template to use
            retriever: Optional retriever to use
            **kwargs: Additional arguments to pass to the chain

        Returns:
            str: Generated response
        """
        chain = self.create_rag_chain(prompt_template, retriever)
        return chain.invoke(question, **kwargs)

    async def aquery(
        self,
        question: str,
        prompt_template: Optional[str] = None,
        retriever: Optional[BaseRetriever] = None,
        **kwargs: Any,
    ) -> str:
        """Query the RAG system asynchronously.

        Args:
            question: Question to ask
            prompt_template: Optional prompt template to use
            retriever: Optional retriever to use
            **kwargs: Additional arguments to pass to the chain

        Returns:
            str: Generated response
        """
        chain = await self.acreate_rag_chain(prompt_template, retriever)
        return await chain.ainvoke(question, **kwargs) 