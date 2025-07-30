"""
Initializer Module.

This module defines the `Initializer` class, which is responsible for setting up
the necessary components for the LangGraph-based workflow. It handles the initialization
of tools, language models, and workflows, ensuring all configurations are validated
and properly integrated.
"""

# Standard library imports
from typing import Any, Callable, List, Optional, Self

# Third-party imports
from crypto_com_developer_platform_client import Client
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langfuse.callback.langchain import LangchainCallbackHandler
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

# Internal application imports
from crypto_com_agent_client.core.model import Model
from crypto_com_agent_client.core.tools import built_in_tools
from crypto_com_agent_client.core.workflows import GraphWorkflow
from crypto_com_agent_client.lib.types.blockchain_config import BlockchainConfig
from crypto_com_agent_client.lib.types.llm_config import LLMConfig
from crypto_com_agent_client.lib.types.plugins_config import PluginsConfig
from crypto_com_agent_client.lib.valdiation.config_validator import ConfigValidator
from crypto_com_agent_client.plugins.personality.personality_plugin import (
    PersonalityPlugin,
)


class Initializer:
    """
    The `Initializer` class encapsulates the initialization of tools, workflows,
    and external integrations required for the LangGraph system.

    Responsibilities:
        - Validating and setting up LLM and blockchain configurations.
        - Initializing tool functions for use in workflows.
        - Configuring the LangGraph workflow graph.
        - Optionally integrating a LangFuse handler for monitoring.

    Attributes:
        llm_config (dict): The validated LLM configuration.
        blockchain_config (dict): The validated blockchain configuration.
        langfuse (object, optional): An optional handler for LangFuse callbacks.
        tools (list[BaseTool]): A list of initialized tools for use in the workflow.
        workflow (CompiledStateGraph): The compiled LangGraph workflow instance.

    Example:
        >>> from lib.initializer import Initializer
        >>> initializer = Initializer(
        ...     llm_config={
        ...         "provider": "OpenAI",
        ...         "model": "gpt-4",
        ...         "provider-api-key": "your-api-key",
        ...         "temperature": 0,
        ...     },
        ...     blockchain_config={
        ...         "chainId": "240",
        ...         "explorer-api-key": "blockchain-api-key",
        ...     },
        ...     langfuse=None
        ... )
        >>> workflow = initializer.workflow
    """

    def __init__(
        self: Self,
        llm_config: LLMConfig,
        blockchain_config: BlockchainConfig,
        plugins: Optional[PluginsConfig] = None,
    ) -> None:
        """
        Initialize the Initializer instance.

        Args:
            llm_config (dict): Configuration for the LLM provider.
                Example:
                    {
                        "provider": "OpenAI",
                        "model": "gpt-4",
                        "provider-api-key": "your-api-key"
                        "temperature": 0,
                    }
            blockchain_config (dict): Configuration for the blockchain client.
                Example:
                    {
                        "chainId": "240",
                        "explorer-api-key": "blockchain-api-key"
                    }
            personality (dict, optional): Personality settings for customizing the assistant's tone and style.
                Example:
                    {
                        "tone": "friendly",
                        "language": "English",
                        "verbosity": "high",
                    }
            instructions (str, optional): Custom instructions for the assistant's behavior.
                Example: "You are a humorous assistant that includes jokes in responses."
            tools (list[callable], optional): List of user-defined tool functions.
            langfuse (object, optional): An optional LangFuse handler for monitoring.

        Attributes:
            llm_config (dict): LLM configuration.
            blockchain_config (dict): Blockchain configuration.
            personality (dict): Personality settings.
            instructions (str): Custom instructions for the model.
            tools (list[BaseTool]): Initialized tool functions.
            langfuse (object, optional): Optional LangFuse handler.

        Raises:
            ValueError: If any required configuration is missing or invalid.

        Example:
            >>> initializer = Initializer(
            ...     llm_config={"provider": "OpenAI", "model": "gpt-4", "provider-api-key": "your-api-key"},
            ...     blockchain_config={"chainId": "240", "explorer-api-key": "blockchain-api-key"},
            ...     personality={"tone": "friendly", "language": "English", "verbosity": "high"},
            ...     instructions="You are a helpful assistant.",
            ...     tools=[custom_tool],
            ... )
        """
        # Validate and store configurations
        self.llm_config: LLMConfig = ConfigValidator.validate_llm_config(llm_config)
        self.blockchain_config: BlockchainConfig = (
            ConfigValidator.validate_blockchain_config(blockchain_config)
        )
        self.plugins = ConfigValidator.validate_plugins_config(plugins)
        plugins.langfuse = ConfigValidator.validate_langfuse_config(plugins.langfuse)

        # Initialize langfuse manager
        self.langfuse: Optional[LangchainCallbackHandler] = plugins.langfuse

        # Initialize personality manager
        self.personality: PersonalityPlugin = PersonalityPlugin(
            personality=plugins.personality,
            instructions=plugins.instructions,
        )

        # Initialize tools and workflow
        self.tools: List[BaseTool] = self._initialize_tools(plugins.tools)
        self.workflow: CompiledStateGraph = self._initialize_graph_workflow()

    def _initialize_tools(
        self: Self, tools: Optional[List[Callable[..., Any]]]
    ) -> List[BaseTool]:
        """
        Initialize and configure tool functions for the ToolNode.

        Args:
            tools (list[callable], optional): List of user-defined tool functions.

        This method sets up blockchain-related tools and initializes the
        Crypto.com developer platform client.

        Returns:
            list[BaseTool]: A list of tools representing functional capabilities
                            for interacting with external systems.

        Example:
            >>> tools = initializer._initialize_tools()
            >>> print(tools)
        """
        # Initialize the blockchain client
        Client.init(
            api_key=self.blockchain_config.explorer_api_key,
            chain_id=self.blockchain_config.chainId,
        )

        # Include built-in and custom tools
        return built_in_tools + (tools or [])

    def _initialize_graph_workflow(self: Self) -> CompiledStateGraph:
        """
        Initialize and return the compiled GraphWorkflow instance.

        This method sets up the LangGraph workflow graph by:
            - Integrating tools for tool interactions.
            - Configuring the language model with the specified provider.
            - Optionally incorporating a LangFuse handler for monitoring.

        Returns:
            CompiledStateGraph: The compiled workflow graph ready for execution.

        Example:
            >>> workflow = initializer._initialize_graph_workflow()
            >>> print(workflow)
        """
        # Wrap tools in a ToolNode
        tool_node: ToolNode = ToolNode(self.tools)

        # Load personality and instructions
        instructions = self.personality.get_configuration()

        # Initialize the language model with the specified provider and API key
        model_handler: Model = Model(
            api_key=self.llm_config.provider_api_key,
            provider=self.llm_config.provider,
            model=self.llm_config.model,
            temperature=self.llm_config.temperature,
            project_id=self.llm_config.project_id,
            location_id=self.llm_config.location_id,
        )

        # Bind tools to the language model
        workflow_model: Runnable[LanguageModelInput, BaseMessage] = (
            model_handler.bind_tools(self.tools)
        )

        # Set up the LangGraph workflow
        graph_workflow: GraphWorkflow = GraphWorkflow(
            model=workflow_model,
            instructions=instructions,
            langfuse=self.langfuse,
            tool_node=tool_node,
        )

        # Compile the workflow and return it
        return graph_workflow.compile(checkpointer=MemorySaver())
