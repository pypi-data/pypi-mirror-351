"""
ReAct (Reasoning + Acting) Agent implementation
"""

import json
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..core.agent import Agent, AgentConfig, AgentResponse
from ..core.tools import get_tool_registry

logger = logging.getLogger(__name__)


@dataclass
class ReActStep:
    """Represents a single ReAct step"""
    iteration: int
    thought: str
    action: str
    action_input: Dict[str, Any]
    observation: str
    timestamp: float


class ReActAgent(Agent):
    """ReAct agent for reasoning and acting"""
    
    def __init__(self, config: AgentConfig):
        # Set default system prompt if not provided
        if not config.system_prompt:
            config.system_prompt = self._get_default_system_prompt()
        
        super().__init__(config)
        self.steps: List[ReActStep] = []
    
    def _get_default_system_prompt(self) -> str:
        """Get the default ReAct system prompt"""
        available_tools = get_tool_registry().list_tools()
        
        prompt = """You are a ReAct (Reasoning + Acting) agent. You help users solve problems by reasoning about them step by step and taking appropriate actions.

You MUST respond with valid JSON in this exact format:
{
  "thought": "Your reasoning about what to do next",
  "action": "action_name",
  "action_input": {
    "parameter_name": "parameter_value"
  }
}

Available actions:
"""
        
        # Add available tools
        for tool_name in available_tools:
            try:
                tool_info = get_tool_registry().get_tool(tool_name)
                schema = get_tool_registry().get_tool_schema(tool_name)
                
                prompt += f"\n- {tool_name}: {tool_info.description if tool_info else 'No description'}"
                
                if schema.get("properties"):
                    prompt += " Parameters: {"
                    params = []
                    for param_name, param_info in schema["properties"].items():
                        required = param_name in schema.get("required", [])
                        param_str = f'"{param_name}": "{param_info.get("type", "string")}"'
                        if required:
                            param_str += " [required]"
                        params.append(param_str)
                    prompt += ", ".join(params) + "}"
            except Exception as e:
                logger.warning(f"Error getting info for tool {tool_name}: {e}")
        
        prompt += """
- finish: {"answer": "your final answer"} - Use this when you have the final answer

Continue this cycle until you can provide a final answer using the 'finish' action.

IMPORTANT: 
- Always think step by step
- Use tools when you need information or to perform actions
- Be thorough in your reasoning
- When you have enough information to answer the question, use the 'finish' action
"""
        
        return prompt
    
    def process(self, input_text: str, **kwargs) -> AgentResponse:
        """Process input using ReAct methodology"""
        try:
            # Clear previous steps
            self.steps = []
            
            # Add user message
            self.add_message("user", f"Problem: {input_text}")
            
            max_iterations = kwargs.get("max_iterations", self.config.max_iterations)
            timeout_seconds = kwargs.get("timeout_seconds", self.config.timeout_seconds)
            start_time = time.time()
            
            for iteration in range(max_iterations):
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    return AgentResponse(
                        content="Timeout reached during processing",
                        metadata={"steps": [step.__dict__ for step in self.steps]},
                        success=False,
                        error="Timeout reached"
                    )
                
                try:
                    # Generate structured response
                    schema = {
                        "type": "object",
                        "properties": {
                            "thought": {
                                "type": "string",
                                "description": "The reasoning about what to do next"
                            },
                            "action": {
                                "type": "string",
                                "description": "The action to take"
                            },
                            "action_input": {
                                "type": "object",
                                "description": "The input parameters for the action"
                            }
                        },
                        "required": ["thought", "action", "action_input"],
                        "additionalProperties": False
                    }
                    
                    llm_response = self._generate_structured_response(
                        self.conversation_history,
                        schema,
                        temperature=self.config.temperature
                    )
                    
                    # Parse the response
                    try:
                        parsed_response = json.loads(llm_response.content)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        # Try to extract JSON from the response
                        parsed_response = self._extract_json_from_text(llm_response.content)
                        if not parsed_response:
                            return AgentResponse(
                                content="Failed to parse agent response",
                                metadata={"steps": [step.__dict__ for step in self.steps]},
                                success=False,
                                error=f"JSON parsing error: {e}"
                            )
                    
                    thought = parsed_response.get("thought", "")
                    action = parsed_response.get("action", "")
                    action_input = parsed_response.get("action_input", {})
                    
                    logger.info(f"Iteration {iteration + 1}: {action}")
                    
                    # Execute the action
                    if action == "finish":
                        final_answer = action_input.get("answer", "Task completed")
                        
                        step = ReActStep(
                            iteration=iteration + 1,
                            thought=thought,
                            action=action,
                            action_input=action_input,
                            observation=final_answer,
                            timestamp=time.time()
                        )
                        self.steps.append(step)
                        
                        return AgentResponse(
                            content=final_answer,
                            metadata={
                                "steps": [step.__dict__ for step in self.steps],
                                "iterations": iteration + 1,
                                "total_time": time.time() - start_time
                            },
                            usage=llm_response.usage,
                            success=True
                        )
                    
                    # Execute tool
                    observation = self.execute_tool(action, **action_input)
                    
                    # Create step
                    step = ReActStep(
                        iteration=iteration + 1,
                        thought=thought,
                        action=action,
                        action_input=action_input,
                        observation=observation,
                        timestamp=time.time()
                    )
                    self.steps.append(step)
                    
                    # Add to conversation history
                    self.add_message("assistant", llm_response.content)
                    self.add_message("user", f"Observation: {observation}")
                    
                except Exception as e:
                    logger.error(f"Error in iteration {iteration + 1}: {e}")
                    return AgentResponse(
                        content="Error during processing",
                        metadata={"steps": [step.__dict__ for step in self.steps]},
                        success=False,
                        error=str(e)
                    )
            
            # Max iterations reached
            return AgentResponse(
                content="Maximum iterations reached. The problem may require a different approach or more complex reasoning.",
                metadata={
                    "steps": [step.__dict__ for step in self.steps],
                    "iterations": max_iterations,
                    "total_time": time.time() - start_time
                },
                success=False,
                error="Maximum iterations reached"
            )
            
        except Exception as e:
            logger.error(f"Error in ReAct agent: {e}")
            return AgentResponse(
                content="",
                success=False,
                error=str(e)
            )
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Try to extract JSON from text that might contain other content"""
        import re
        
        # Look for JSON-like structures
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        return None
    
    def get_steps_summary(self) -> str:
        """Get a summary of all ReAct steps"""
        if not self.steps:
            return "No steps recorded"
        
        summary = "ReAct Steps Summary:\n"
        summary += "=" * 50 + "\n"
        
        for step in self.steps:
            summary += f"\nStep {step.iteration}:\n"
            summary += f"Thought: {step.thought}\n"
            summary += f"Action: {step.action}\n"
            summary += f"Action Input: {step.action_input}\n"
            summary += f"Observation: {step.observation}\n"
            summary += "-" * 30 + "\n"
        
        return summary


def create_react_agent(name: str, **kwargs) -> ReActAgent:
    """Create a ReAct agent"""
    config = AgentConfig(
        name=name,
        **kwargs
    )
    return ReActAgent(config) 