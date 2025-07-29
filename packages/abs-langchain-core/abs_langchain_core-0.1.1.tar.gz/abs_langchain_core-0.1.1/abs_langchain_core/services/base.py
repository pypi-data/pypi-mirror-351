from typing import Optional, Dict, Any, List, Union
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ..core.llm_provider import LLMProvider
from ..core.logger import UsageLogger


class BaseService:
    """Base service for all LangChain operations."""

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        logger: Optional[UsageLogger] = None,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize the base service.

        Args:
            model_name: Name of the model to use
            temperature: Temperature for generation
            logger: Optional usage logger
            system_prompt: Optional system prompt to use
            **kwargs: Additional arguments to pass to the model
        """
        self.llm_provider = LLMProvider(
            model_name=model_name,
            temperature=temperature,
            logger=logger,
            **kwargs,
        )
        self.system_prompt = system_prompt
        self.logger = logger

    def _create_messages(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        history: Optional[List[BaseMessage]] = None,
    ) -> List[BaseMessage]:
        """Create a list of messages for the chat model.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to override the default
            history: Optional message history

        Returns:
            List[BaseMessage]: List of messages
        """
        messages = []
        
        # Add system message if provided
        if system_prompt or self.system_prompt:
            messages.append(
                SystemMessage(content=system_prompt or self.system_prompt)
            )

        # Add history if provided
        if history:
            messages.extend(history)

        # Add the current prompt
        messages.append(HumanMessage(content=prompt))

        return messages

    def _create_chain(self, prompt_template: Optional[str] = None):
        """Create a basic chain with the given prompt template.

        Args:
            prompt_template: Optional prompt template to use

        Returns:
            Chain: Configured chain
        """
        if prompt_template:
            prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt or "You are a helpful AI assistant."),
                ("human", "{input}")
            ])

        return prompt | self.llm_provider.get_chat_model() | StrOutputParser()

    async def _acreate_chain(self, prompt_template: Optional[str] = None):
        """Create an async chain with the given prompt template.

        Args:
            prompt_template: Optional prompt template to use

        Returns:
            Chain: Configured async chain
        """
        if prompt_template:
            prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt or "You are a helpful AI assistant."),
                ("human", "{input}")
            ])

        # Get the chat model asynchronously
        chat_model = await self.llm_provider.aget_chat_model()
        return prompt | chat_model | StrOutputParser()

    def _get_metadata(self, **kwargs) -> Dict[str, Any]:
        """Get metadata for logging.

        Args:
            **kwargs: Additional metadata to include

        Returns:
            Dict[str, Any]: Metadata dictionary
        """
        metadata = {
            "model_name": self.llm_provider.model_name,
            "temperature": self.llm_provider.temperature,
            **kwargs,
        }
        return metadata 