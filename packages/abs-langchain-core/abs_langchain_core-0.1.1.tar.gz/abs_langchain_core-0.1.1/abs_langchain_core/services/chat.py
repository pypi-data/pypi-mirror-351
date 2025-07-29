from typing import Optional, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.memory import BaseMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .base import BaseService
from ..core.logger import UsageLogger


class ChatService(BaseService):
    """Service for chat-based LLM interactions."""

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        logger: Optional[UsageLogger] = None,
        system_prompt: Optional[str] = None,
        memory: Optional[BaseMemory] = None,
        **kwargs: Any,
    ):
        """Initialize the chat service.

        Args:
            model_name: Name of the model to use
            temperature: Temperature for generation
            logger: Optional usage logger
            system_prompt: Optional system prompt to use
            memory: Optional memory component for conversation history
            **kwargs: Additional arguments to pass to the model
        """
        super().__init__(
            model_name=model_name,
            temperature=temperature,
            logger=logger,
            system_prompt=system_prompt or "You are a helpful AI assistant.",
            **kwargs,
        )
        self.memory = memory

    def create_chat_chain(
        self,
        prompt_template: Optional[str] = None,
    ):
        """Create a chat chain.

        Args:
            prompt_template: Optional prompt template to use

        Returns:
            Chain: Configured chat chain
        """
        # Create prompt template
        if prompt_template:
            prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input}")
            ])

        # Create chain
        chain = prompt | self.llm_provider.get_chat_model() | StrOutputParser()

        return chain

    async def acreate_chat_chain(
        self,
        prompt_template: Optional[str] = None,
    ):
        """Create an async chat chain.

        Args:
            prompt_template: Optional prompt template to use

        Returns:
            Chain: Configured async chat chain
        """
        # Create prompt template
        if prompt_template:
            prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input}")
            ])

        # Create chain
        chain = prompt | self.llm_provider.aget_chat_model() | StrOutputParser()

        return chain

    def chat(
        self,
        message: str,
        prompt_template: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Send a message to the chat model.

        Args:
            message: Message to send
            prompt_template: Optional prompt template to use
            **kwargs: Additional arguments to pass to the chain

        Returns:
            str: Model's response
        """
        # Get history if memory is available
        history = []
        if self.memory:
            history = self.memory.chat_memory.messages

        # Create messages
        messages = self._create_messages(message, history=history)

        # Create and run chain
        chain = self.create_chat_chain(prompt_template)
        response = chain.invoke({"input": message}, **kwargs)

        # Update memory if available
        if self.memory:
            self.memory.chat_memory.add_user_message(message)
            self.memory.chat_memory.add_ai_message(response)

        return response

    async def achat(
        self,
        message: str,
        prompt_template: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Send a message to the chat model asynchronously.

        Args:
            message: Message to send
            prompt_template: Optional prompt template to use
            **kwargs: Additional arguments to pass to the chain

        Returns:
            str: Model's response
        """
        # Get history if memory is available
        history = []
        if self.memory:
            history = self.memory.chat_memory.messages

        # Create messages
        messages = self._create_messages(message, history=history)

        # Create and run chain
        chain = await self.acreate_chat_chain(prompt_template)
        response = await chain.ainvoke({"input": message}, **kwargs)

        # Update memory if available
        if self.memory:
            self.memory.chat_memory.add_user_message(message)
            self.memory.chat_memory.add_ai_message(response)

        return response

    def get_chat_history(self) -> List[BaseMessage]:
        """Get the chat history.

        Returns:
            List[BaseMessage]: List of messages in the chat history
        """
        if not self.memory:
            return []
        return self.memory.chat_memory.messages

    def clear_chat_history(self) -> None:
        """Clear the chat history."""
        if self.memory:
            self.memory.chat_memory.clear() 