from _typeshed import Incomplete
from a2a.server.agent_execution import RequestContext as RequestContext
from a2a.server.events.event_queue import EventQueue as EventQueue
from a2a.server.tasks import TaskUpdater as TaskUpdater
from gllm_agents.a2a.server.base_executor import BaseA2AExecutor as BaseA2AExecutor
from gllm_agents.agent.langgraph_agent import LangGraphAgent as LangGraphAgent
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete

class LangGraphA2AExecutor(BaseA2AExecutor):
    """A2A Executor for serving a `LangGraphAgent`.

    This executor bridges the A2A server protocol with a `gllm_agents.agent.LangGraphAgent`.
    It handles incoming requests by invoking the agent's `arun_a2a_stream` method,
    processes the streamed dictionary chunks, and formats them into A2A compliant events.
    It leverages common functionality from `BaseA2AExecutor` for task management,
    initial request checks, and cancellation.

    Attributes:
        agent (LangGraphAgent): The instance of `LangGraphAgent` to be executed.
    """
    agent: LangGraphAgent
    def __init__(self, langgraph_agent_instance: LangGraphAgent) -> None:
        """Initializes the LangGraphA2AExecutor.

        Args:
            langgraph_agent_instance (LangGraphAgent): A fully initialized instance
                of `LangGraphAgent`.

        Raises:
            TypeError: If `langgraph_agent_instance` is not an instance of `LangGraphAgent`.
        """
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Processes an incoming agent request using the `LangGraphAgent`.

        This method first performs initial checks using `_handle_initial_execute_checks`.
        If successful, it prepares the `_process_stream` coroutine and passes it to
        `_execute_agent_processing` from the base class to manage its lifecycle.
        The `_process_stream` method is responsible for calling the agent's
        `arun_a2a_stream` and handling its output.

        Args:
            context (RequestContext): The A2A request context containing message details,
                task ID, and context ID.
            event_queue (EventQueue): The queue for sending A2A events (task status,
                artifacts) back to the server.
        """
