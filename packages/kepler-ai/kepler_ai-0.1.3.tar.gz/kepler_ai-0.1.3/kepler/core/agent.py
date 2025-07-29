"""
Core agent system for Kepler framework
"""

import json
import time
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from .config import get_config
from .llm_providers import LLMProvider, LLMProviderFactory, LLMResponse
from .tools import ToolRegistry, get_tool_registry

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Response from an agent"""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    usage: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class AgentConfig:
    """Configuration for an agent"""
    name: str
    provider: str = "openai"
    model: str = None
    max_iterations: int = None
    timeout_seconds: int = None
    temperature: float = 0.1
    system_prompt: str = ""
    tools: List[str] = field(default_factory=list)
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    """Base class for all agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.global_config = get_config()
        
        # Set defaults from global config
        if config.max_iterations is None:
            config.max_iterations = self.global_config.max_iterations
        if config.timeout_seconds is None:
            config.timeout_seconds = self.global_config.timeout_seconds
        
        # Initialize LLM provider
        self.llm_provider = LLMProviderFactory.create_provider(
            config.provider, 
            config.model
        )
        
        # Initialize tool registry
        self.tool_registry = get_tool_registry()
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # Add system prompt if provided
        if config.system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": config.system_prompt
            })
        
        logger.info(f"Initialized agent: {config.name} with provider: {config.provider}")
    
    @abstractmethod
    def process(self, input_text: str, **kwargs) -> AgentResponse:
        """Process input and return response"""
        pass
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def clear_history(self):
        """Clear conversation history (keeping system prompt)"""
        system_messages = [msg for msg in self.conversation_history if msg["role"] == "system"]
        self.conversation_history = system_messages
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools for this agent"""
        if self.config.tools:
            return self.config.tools
        return self.tool_registry.list_tools()
    
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool and return result"""
        try:
            if self.config.tools and tool_name not in self.config.tools:
                return f"Error: Tool '{tool_name}' not available for this agent"
            
            result = self.tool_registry.execute_tool(tool_name, **kwargs)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing tool {tool_name}: {str(e)}"
    
    def _generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using LLM provider"""
        try:
            return self.llm_provider.generate(messages, **kwargs)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _generate_structured_response(self, messages: List[Dict[str, str]], schema: Dict[str, Any], **kwargs) -> LLMResponse:
        """Generate structured response using LLM provider"""
        try:
            return self.llm_provider.generate_structured(messages, schema, **kwargs)
        except Exception as e:
            logger.error(f"Error generating structured response: {e}")
            raise


class SimpleAgent(Agent):
    """Simple agent that processes input and returns response"""
    
    def process(self, input_text: str, **kwargs) -> AgentResponse:
        """Process input and return response"""
        try:
            # Add user message
            self.add_message("user", input_text)
            
            # Generate response
            llm_response = self._generate_response(
                self.conversation_history,
                temperature=self.config.temperature,
                **kwargs
            )
            
            # Add assistant response to history
            self.add_message("assistant", llm_response.content)
            
            return AgentResponse(
                content=llm_response.content,
                metadata=llm_response.metadata or {},
                usage=llm_response.usage,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return AgentResponse(
                content="",
                success=False,
                error=str(e)
            )


class ToolAgent(Agent):
    """Agent that can use tools"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        
        # Add tool information to system prompt
        if not config.system_prompt:
            self.config.system_prompt = self._generate_tool_system_prompt()
            self.conversation_history = [{
                "role": "system",
                "content": self.config.system_prompt
            }]
    
    def _generate_tool_system_prompt(self) -> str:
        """Generate system prompt with tool information"""
        available_tools = self.get_available_tools()
        
        prompt = """You are a helpful AI assistant with access to tools. You can use these tools to help answer questions and complete tasks.

Available tools:
"""
        
        for tool_name in available_tools:
            try:
                schema = self.tool_registry.get_tool_schema(tool_name)
                tool_info = self.tool_registry.get_tool(tool_name)
                prompt += f"\n- {tool_name}: {tool_info.description if tool_info else 'No description'}"
                
                if schema.get("properties"):
                    prompt += "\n  Parameters:"
                    for param_name, param_info in schema["properties"].items():
                        required = param_name in schema.get("required", [])
                        prompt += f"\n    - {param_name} ({param_info.get('type', 'string')})"
                        if required:
                            prompt += " [required]"
                        if param_info.get("description"):
                            prompt += f": {param_info['description']}"
            except Exception as e:
                logger.warning(f"Error getting schema for tool {tool_name}: {e}")
        
        prompt += """

To use a tool, respond with JSON in this format:
{
  "tool_call": {
    "name": "tool_name",
    "parameters": {
      "param1": "value1",
      "param2": "value2"
    }
  },
  "reasoning": "Why you're using this tool"
}

If you don't need to use a tool, just respond normally with your answer.
"""
        
        return prompt
    
    def process(self, input_text: str, **kwargs) -> AgentResponse:
        """Process input with tool support"""
        try:
            # Add user message
            self.add_message("user", input_text)
            
            max_tool_iterations = kwargs.get("max_tool_iterations", 5)
            tool_calls = []
            
            for iteration in range(max_tool_iterations):
                # Generate response
                llm_response = self._generate_response(
                    self.conversation_history,
                    temperature=self.config.temperature,
                    **{k: v for k, v in kwargs.items() if k != "max_tool_iterations"}
                )
                
                # Check if response contains tool call
                tool_call = self._extract_tool_call(llm_response.content)
                
                if tool_call:
                    # Execute tool
                    tool_result = self.execute_tool(
                        tool_call["name"],
                        **tool_call["parameters"]
                    )
                    
                    tool_calls.append({
                        "name": tool_call["name"],
                        "parameters": tool_call["parameters"],
                        "result": tool_result
                    })
                    
                    # Add tool result to conversation
                    self.add_message("assistant", f"Used tool {tool_call['name']}: {tool_result}")
                    self.add_message("user", "Please continue with your response based on the tool result.")
                else:
                    # No tool call, this is the final response
                    self.add_message("assistant", llm_response.content)
                    
                    return AgentResponse(
                        content=llm_response.content,
                        metadata=llm_response.metadata or {},
                        tool_calls=tool_calls,
                        usage=llm_response.usage,
                        success=True
                    )
            
            # Max iterations reached
            return AgentResponse(
                content="Maximum tool iterations reached. Please try a simpler request.",
                tool_calls=tool_calls,
                success=False,
                error="Maximum tool iterations reached"
            )
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return AgentResponse(
                content="",
                success=False,
                error=str(e)
            )
    
    def _extract_tool_call(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract tool call from response content"""
        try:
            # Try to parse as JSON
            parsed = json.loads(content.strip())
            
            if "tool_call" in parsed:
                tool_call = parsed["tool_call"]
                return {
                    "name": tool_call["name"],
                    "parameters": tool_call.get("parameters", {})
                }
        except json.JSONDecodeError:
            pass
        
        return None


# Agent factory functions
def create_agent(name: str, 
                agent_type: str = "simple",
                provider: str = "openai",
                model: str = None,
                system_prompt: str = "",
                tools: List[str] = None,
                **kwargs) -> Agent:
    """Create an agent with the specified configuration"""
    
    config = AgentConfig(
        name=name,
        provider=provider,
        model=model,
        system_prompt=system_prompt,
        tools=tools or [],
        **kwargs
    )
    
    if agent_type == "simple":
        return SimpleAgent(config)
    elif agent_type == "tool":
        return ToolAgent(config)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


def create_simple_agent(name: str, **kwargs) -> SimpleAgent:
    """Create a simple agent"""
    return create_agent(name, agent_type="simple", **kwargs)


def create_tool_agent(name: str, **kwargs) -> ToolAgent:
    """Create a tool-enabled agent"""
    return create_agent(name, agent_type="tool", **kwargs)


# Function-based agent creation
def agent_function(name: str = None,
                  provider: str = "openai",
                  model: str = None,
                  system_prompt: str = "",
                  tools: List[str] = None,
                  agent_type: str = "tool"):
    """Decorator to create an agent function"""
    
    def decorator(func: Callable) -> Callable:
        agent_name = name or func.__name__
        
        # Create agent
        agent = create_agent(
            name=agent_name,
            agent_type=agent_type,
            provider=provider,
            model=model,
            system_prompt=system_prompt or func.__doc__ or "",
            tools=tools
        )
        
        def wrapper(input_text: str, **kwargs) -> AgentResponse:
            return agent.process(input_text, **kwargs)
        
        # Store agent reference
        wrapper.agent = agent
        wrapper.__name__ = agent_name
        wrapper.__doc__ = func.__doc__
        
        return wrapper
    
    return decorator 