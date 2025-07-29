from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.callbacks import CallbackManager
from langchain_core.messages import BaseMessage

from ..callbacks.token_tracker import TokenTrackingCallback
from ..core.logger import UsageLogger


class LLMProvider:
    """Provider for LangChain LLM models with token tracking."""

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        logger: Optional[UsageLogger] = None,
        callbacks: Optional[List[Any]] = None,
        **kwargs: Any,
    ):
        """Initialize the LLM provider.

        Args:
            model_name: Name of the model to use
            temperature: Temperature for generation
            logger: Optional usage logger
            callbacks: Additional callbacks to use
            **kwargs: Additional arguments to pass to the model
        """
        self.model_name = model_name
        self.temperature = temperature
        self.logger = logger
        self.kwargs = kwargs

        # Initialize callbacks
        self.callbacks = callbacks or []
        if logger:
            self.callbacks.append(
                TokenTrackingCallback(
                    logger=logger,
                    operation_type="llm",
                    metadata={"model_name": model_name, "temperature": temperature},
                )
            )

    def get_chat_model(self) -> BaseChatModel:
        """Get a chat model instance with configured callbacks.

        Returns:
            BaseChatModel: Configured chat model instance
        """
        return ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            callbacks=self.callbacks,
            return_token_usage=True,  # Enable token usage tracking
            **self.kwargs,
        )

    async def aget_chat_model(self) -> BaseChatModel:
        """Get an async chat model instance with configured callbacks.

        Returns:
            BaseChatModel: Configured async chat model instance
        """
        return ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            callbacks=self.callbacks,
            streaming=True,  # Enable streaming for async
            stream_usage=True,  # Enable token usage tracking
            **self.kwargs,
        )

    def get_embedding_model(self):
        """Get an embedding model instance.

        Returns:
            Embedding model instance
        """
        # TODO: Implement embedding model provider
        raise NotImplementedError("Embedding model provider not implemented yet")

    def get_completion_model(self):
        """Get a completion model instance.

        Returns:
            Completion model instance
        """
        # TODO: Implement completion model provider
        raise NotImplementedError("Completion model provider not implemented yet") 