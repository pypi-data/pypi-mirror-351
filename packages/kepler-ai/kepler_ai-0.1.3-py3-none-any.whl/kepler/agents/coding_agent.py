"""
Coding Agent - Specialized ReAct agent for coding tasks
"""

from typing import List
from ..core.agent import AgentConfig
from .react_agent import ReActAgent


class CodingAgent(ReActAgent):
    """Specialized agent for coding tasks"""
    
    def __init__(self, config: AgentConfig):
        # Set coding-specific tools if not specified
        if not config.tools:
            config.tools = [
                "write_file",
                "read_file", 
                "list_files",
                "execute_python",
                "search_web"
            ]
        
        # Set coding-specific system prompt if not provided
        if not config.system_prompt:
            config.system_prompt = self._get_coding_system_prompt()
        
        super().__init__(config)
    
    def _get_coding_system_prompt(self) -> str:
        """Get system prompt optimized for coding tasks"""
        return """You are a ReAct (Reasoning + Acting) coding agent. You help users solve coding problems by reasoning about them step by step and taking appropriate actions.

You MUST respond with valid JSON in this exact format:
{
  "thought": "Your reasoning about what to do next",
  "action": "action_name", 
  "action_input": {
    "parameter_name": "parameter_value"
  }
}

Available actions for coding tasks:
- write_file: {"filename": "path/to/file", "content": "file content"} - Write code to a file
- read_file: {"filename": "path/to/file"} - Read existing code files
- list_files: {"directory": "path/to/directory"} - List files in a directory
- execute_python: {"code": "python code"} - Execute Python code and see output
- search_web: {"query": "search query", "num_results": 10} - Search for coding solutions and documentation
- finish: {"answer": "your final answer"} - Use this when you have completed the coding task

For comprehensive coding tasks, follow this enhanced workflow:
1. Understand the requirements clearly
2. Search for relevant documentation, examples, and best practices
3. Plan the code structure and architecture
4. Write well-documented, production-ready code
5. Test the implementation thoroughly
6. Provide clear explanations and usage instructions

IMPORTANT Guidelines:
- Always write clean, well-documented code with proper error handling
- Include comprehensive comments explaining the logic
- Follow best practices and coding standards
- Test your code before providing the final answer
- Consider edge cases and potential issues
- Provide usage examples and documentation
- When researching, look for official documentation and reliable sources
- Be thorough in your implementation and testing

Continue this cycle until you can provide a final answer using the 'finish' action.
"""


def create_coding_agent(name: str, **kwargs) -> CodingAgent:
    """Create a coding agent"""
    config = AgentConfig(
        name=name,
        **kwargs
    )
    return CodingAgent(config) 