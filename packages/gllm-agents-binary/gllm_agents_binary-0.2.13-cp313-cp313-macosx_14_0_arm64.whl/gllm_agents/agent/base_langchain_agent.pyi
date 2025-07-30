import abc
from _typeshed import Incomplete
from gllm_agents.agent.base_agent import BaseAgent as BaseAgent
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from langchain_core.messages import BaseMessage as BaseMessage
from typing import Any

logger: Incomplete

class BaseLangChainAgent(BaseAgent, metaclass=abc.ABCMeta):
    """Base class for langchain-based agents, providing common functions for LangGraphAgent and LangChainAgent.

    This class extends BaseAgent and provides additional functionality specific to langchain-based agents.
    The common functionality includes:
    - Extracting output from various state formats (dict, list)
    - Handling LangChain message types (AIMessage, ToolMessage)
    - Common state management for LangChain agents
    """
    def __init__(self, name: str, instruction: str, description: str | None = None, **kwargs: Any) -> None:
        """Initialize the BaseLangChainAgent.

        Args:
            name: The name of the agent
            instruction: The system instruction/prompt for the agent
            description: Optional description of the agent
            **kwargs: Additional keyword arguments passed to BaseAgent
        """
