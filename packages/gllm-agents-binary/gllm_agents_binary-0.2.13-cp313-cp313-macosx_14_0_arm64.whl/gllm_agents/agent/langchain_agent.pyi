from _typeshed import Incomplete
from a2a.types import AgentCard as AgentCard
from gllm_agents.agent.base_langchain_agent import BaseLangChainAgent as BaseLangChainAgent
from gllm_agents.mcp.client import MCPClient as MCPClient
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from langchain_core.messages import BaseMessage as BaseMessage
from langchain_core.tools import BaseTool as BaseTool
from typing import Any, AsyncGenerator, Sequence

logger: Incomplete

class LangChainAgent(BaseLangChainAgent):
    """AgentInterface implementation for LangChain framework.

    This class wraps a LangChain model and optional tools, and internally constructs
    an AgentExecutor. It implements the required run, arun, and arun_stream methods
    for synchronous, asynchronous, and streaming execution.
    """
    llm: Incomplete
    tools: list[BaseTool]
    verbose: Incomplete
    mcp_config: Incomplete
    def __init__(self, name: str, instruction: str, llm: Any, tools: Sequence[BaseTool] | None = None, verbose: bool = False, description: str | None = None, **kwargs: Any) -> None:
        """Initializes a LangChainAgent.

        Args:
            name: Name of the agent.
            instruction: System/system prompt for the agent.
            llm: A LangChain LLM (e.g., ChatOpenAI).
            tools: Optional; list of LangChain tools. Defaults to None (no tools).
            agent_type: LangChain AgentType. Defaults to ZERO_SHOT_REACT_DESCRIPTION.
            verbose: Whether to enable verbose logging for debugging. Defaults to False.
            description: Optional description of the agent.
            **kwargs: Additional keyword arguments passed to AgentInterface.

        Raises:
            RuntimeError: If the internal LangChain AgentExecutor cannot be initialized.
        """
    def run(self, query: str, configurable: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        """Synchronously runs the agent using LangChain.

        This method wraps the asynchronous `arun` method, allowing for synchronous execution.
        If already in an event loop (such as in Jupyter), it will use the running event loop.

        Args:
            query: The user query to process.
            configurable: Optional configuration parameters for the agent such as thread_id.
            **kwargs: Additional keyword arguments to pass to the agent.

        Returns:
            A dictionary containing at least the 'output' key with the agent's response.

        Raises:
            RuntimeError: If the agent fails to process the query.
        """
    async def arun(self, query: str, configurable: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        """Asynchronously runs the agent using LangChain AgentExecutor.

        This method sends the query to the agent and returns the result as a dictionary.

        Args:
            query: The user query to process.
            configurable: Optional configuration parameters for the agent such as thread_id.
            **kwargs: Additional keyword arguments to pass to the agent.

        Returns:
            A dictionary containing at least the 'output' key with the agent's response.

        Raises:
            RuntimeError: If the agent fails to process the query or cannot determine input format.
        """
    async def arun_stream(self, query: str, configurable: dict[str, Any] | None = None, **kwargs: Any) -> AsyncGenerator[str | dict[str, Any], None]:
        """Asynchronously streams the agent's response.

        If MCP configuration exists, connects to the MCP server and registers tools before streaming.

        Args:
            query: The input query for the agent.
            configurable: Dictionary for configuration, or None.
            **kwargs: Additional keyword arguments to pass to the agent.

        Yields:
            Output chunks from the agent, either as strings or dictionaries.
        """
    def register_a2a_agents(self, agent_cards: list[AgentCard]) -> None:
        """Registers A2A agents as tools for this LangChain agent."""
    async def arun_a2a_stream(self, query: str, configurable: dict[str, Any] | None = None, **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]:
        '''Asynchronously streams the agent\'s response in a generic format for A2A.

        Args:
            query: The input query for the agent.
            configurable: Optional configuration parameters for the agent such as thread_id.
            **kwargs: Additional keyword arguments.

        Yields:
            Dictionaries with "status" and "content" keys.
            Possible statuses: "working", "completed", "failed", "canceled".
        '''
