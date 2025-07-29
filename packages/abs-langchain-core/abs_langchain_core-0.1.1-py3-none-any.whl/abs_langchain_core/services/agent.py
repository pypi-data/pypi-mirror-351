from typing import Optional, List, Dict, Any, Type
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.tools import Tool as LangChainTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


from .base import BaseService
from ..core.logger import UsageLogger

from abs_utils.logger import setup_logger

logger = setup_logger(__name__)

class AgentService(BaseService):
    """Service for LangChain agent operations."""

    def __init__(
        self,
        tools: List[LangChainTool],
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        logger: Optional[UsageLogger] = None,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize the agent service.

        Args:
            tools: List of tools for the agent to use
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
            system_prompt=system_prompt or "You are a helpful AI assistant that can use tools to help answer questions.",
            **kwargs,
        )
        self.tools = tools

    def create_agent(
        self,
        prompt_template: Optional[str] = None,
        agent_type: Optional[Type] = None,
        **kwargs: Any,
    ) -> AgentExecutor:
        """Create an agent executor.

        Args:
            prompt_template: Optional prompt template to use
            agent_type: Optional agent type to use
            **kwargs: Additional arguments to pass to the agent

        Returns:
            AgentExecutor: Configured agent executor
        """
        # Create prompt template
        if prompt_template:
            prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm_provider.get_chat_model(),
            tools=self.tools,
            prompt=prompt,
        )

        # Create executor
        executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=True,
            **kwargs,
        )

        return executor

    async def acreate_agent(
        self,
        prompt_template: Optional[str] = None,
        agent_type: Optional[Type] = None,
        **kwargs: Any,
    ) -> AgentExecutor:
        """Create an async agent executor.

        Args:
            prompt_template: Optional prompt template to use
            agent_type: Optional agent type to use
            **kwargs: Additional arguments to pass to the agent

        Returns:
            AgentExecutor: Configured async agent executor
        """
        # Create prompt template
        if prompt_template:
            prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
        
        logger.info(f"Prompt: {prompt}")

        # Get the chat model asynchronously
        chat_model = await self.llm_provider.aget_chat_model()

        # Create agent
        agent = create_openai_functions_agent(
            llm=chat_model,
            tools=self.tools,
            prompt=prompt,
        )

        # Create executor
        executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=True,
            **kwargs,
        )

        return executor

    def run(
        self,
        input_text: str,
        prompt_template: Optional[str] = None,
        agent_type: Optional[Type] = None,
        **kwargs: Any,
    ) -> str:
        """Run the agent.

        Args:
            input_text: Input text for the agent
            prompt_template: Optional prompt template to use
            agent_type: Optional agent type to use
            **kwargs: Additional arguments to pass to the agent

        Returns:
            str: Agent's response
        """
        executor = self.create_agent(prompt_template, agent_type, **kwargs)
        return executor.invoke({"input": input_text})["output"]

    async def arun(
        self,
        input_text: str,
        prompt_template: Optional[str] = None,
        agent_type: Optional[Type] = None,
        **kwargs: Any,
    ) -> str:
        """Run the agent asynchronously.

        Args:
            input_text: Input text for the agent
            prompt_template: Optional prompt template to use
            agent_type: Optional agent type to use
            **kwargs: Additional arguments to pass to the agent

        Returns:
            str: Agent's response
        """
        executor = await self.acreate_agent(prompt_template, agent_type, **kwargs)
        return (await executor.ainvoke({"input": input_text}))["output"] 