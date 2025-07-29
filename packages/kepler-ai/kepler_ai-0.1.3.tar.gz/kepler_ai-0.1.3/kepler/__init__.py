"""
Kepler Multi-Agent Framework

A powerful, flexible framework for building AI agents with multiple LLM support,
function calling, and ReAct reasoning capabilities.
"""

__version__ = "0.1.3"
__author__ = "Sandeep Chakraborty"
__email__ = "heyitssandeep@gmail.com"

from .core.agent import Agent, create_agent, create_simple_agent, create_tool_agent, agent_function
from .core.llm_providers import LLMProvider, OpenAIProvider, AnthropicProvider, GeminiProvider
from .core.tools import tool, ToolRegistry, get_tool_registry
from .core.config import Config, load_config, set_config
from .agents.react_agent import ReActAgent, create_react_agent
from .agents.coding_agent import CodingAgent, create_coding_agent

__all__ = [
    "Agent",
    "create_agent",
    "create_simple_agent", 
    "create_tool_agent",
    "create_react_agent",
    "create_coding_agent",
    "agent_function",
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider", 
    "GeminiProvider",
    "tool",
    "ToolRegistry",
    "get_tool_registry",
    "Config",
    "load_config",
    "set_config",
    "ReActAgent",
    "CodingAgent"
] 