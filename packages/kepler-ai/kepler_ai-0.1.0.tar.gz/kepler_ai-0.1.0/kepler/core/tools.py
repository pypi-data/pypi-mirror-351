"""
Enhanced tool system for Kepler framework with decorators and automatic registration
"""

import inspect
import json
from typing import Dict, Any, List, Optional, Callable, get_type_hints
from dataclasses import dataclass, field
from functools import wraps
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolParameter:
    """Represents a tool parameter"""
    name: str
    type_hint: type
    description: str = ""
    required: bool = True
    default: Any = None


@dataclass
class ToolInfo:
    """Information about a registered tool"""
    name: str
    function: Callable
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    return_type: type = str
    category: str = "general"


class ToolRegistry:
    """Registry for managing tools"""
    
    def __init__(self):
        self._tools: Dict[str, ToolInfo] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def register(self, 
                 name: str = None,
                 description: str = "",
                 category: str = "general",
                 parameters: Dict[str, str] = None) -> Callable:
        """Decorator to register a function as a tool"""
        
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            
            # Get function signature and type hints
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
            
            # Extract parameters
            tool_parameters = []
            for param_name, param in sig.parameters.items():
                param_type = type_hints.get(param_name, str)
                param_desc = (parameters or {}).get(param_name, "")
                required = param.default == inspect.Parameter.empty
                default_val = None if required else param.default
                
                tool_parameters.append(ToolParameter(
                    name=param_name,
                    type_hint=param_type,
                    description=param_desc,
                    required=required,
                    default=default_val
                ))
            
            # Get return type
            return_type = type_hints.get('return', str)
            
            # Create tool info
            tool_info = ToolInfo(
                name=tool_name,
                function=func,
                description=description or func.__doc__ or "",
                parameters=tool_parameters,
                return_type=return_type,
                category=category
            )
            
            # Register the tool
            self._tools[tool_name] = tool_info
            
            # Add to category
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(tool_name)
            
            logger.info(f"Registered tool: {tool_name} in category: {category}")
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    return f"Error executing {tool_name}: {str(e)}"
            
            return wrapper
        
        return decorator
    
    def get_tool(self, name: str) -> Optional[ToolInfo]:
        """Get tool information by name"""
        return self._tools.get(name)
    
    def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool with given parameters"""
        tool_info = self.get_tool(name)
        if not tool_info:
            raise ValueError(f"Tool '{name}' not found")
        
        # Validate parameters
        validated_kwargs = self._validate_parameters(tool_info, kwargs)
        
        try:
            result = tool_info.function(**validated_kwargs)
            logger.info(f"Successfully executed tool: {name}")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            raise
    
    def _validate_parameters(self, tool_info: ToolInfo, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and convert parameters"""
        validated = {}
        
        for param in tool_info.parameters:
            if param.name in kwargs:
                value = kwargs[param.name]
                # Basic type conversion
                if param.type_hint == int and isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError:
                        raise ValueError(f"Parameter '{param.name}' must be an integer")
                elif param.type_hint == float and isinstance(value, (str, int)):
                    try:
                        value = float(value)
                    except ValueError:
                        raise ValueError(f"Parameter '{param.name}' must be a number")
                elif param.type_hint == bool and isinstance(value, str):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                
                validated[param.name] = value
            elif param.required:
                raise ValueError(f"Required parameter '{param.name}' is missing")
            elif param.default is not None:
                validated[param.name] = param.default
        
        return validated
    
    def list_tools(self, category: str = None) -> List[str]:
        """List available tools, optionally filtered by category"""
        if category:
            return self._categories.get(category, [])
        return list(self._tools.keys())
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return list(self._categories.keys())
    
    def get_tool_schema(self, name: str) -> Dict[str, Any]:
        """Get JSON schema for a tool"""
        tool_info = self.get_tool(name)
        if not tool_info:
            raise ValueError(f"Tool '{name}' not found")
        
        properties = {}
        required = []
        
        for param in tool_info.parameters:
            param_schema = {"description": param.description}
            
            # Map Python types to JSON schema types
            if param.type_hint == str:
                param_schema["type"] = "string"
            elif param.type_hint == int:
                param_schema["type"] = "integer"
            elif param.type_hint == float:
                param_schema["type"] = "number"
            elif param.type_hint == bool:
                param_schema["type"] = "boolean"
            elif param.type_hint == list:
                param_schema["type"] = "array"
            elif param.type_hint == dict:
                param_schema["type"] = "object"
            else:
                param_schema["type"] = "string"  # Default fallback
            
            if param.default is not None:
                param_schema["default"] = param.default
            
            properties[param.name] = param_schema
            
            if param.required:
                required.append(param.name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "description": tool_info.description
        }
    
    def generate_documentation(self) -> str:
        """Generate documentation for all tools"""
        doc = "# Available Tools\n\n"
        
        for category in sorted(self._categories.keys()):
            doc += f"## {category.title()}\n\n"
            
            for tool_name in self._categories[category]:
                tool_info = self._tools[tool_name]
                doc += f"### {tool_name}\n\n"
                doc += f"{tool_info.description}\n\n"
                
                if tool_info.parameters:
                    doc += "**Parameters:**\n\n"
                    for param in tool_info.parameters:
                        required_text = " (required)" if param.required else " (optional)"
                        default_text = f" (default: {param.default})" if param.default is not None else ""
                        doc += f"- `{param.name}` ({param.type_hint.__name__}){required_text}{default_text}: {param.description}\n"
                    doc += "\n"
                
                doc += f"**Returns:** {tool_info.return_type.__name__}\n\n"
                doc += "---\n\n"
        
        return doc


# Global tool registry
_global_registry = ToolRegistry()


def tool(name: str = None, 
         description: str = "",
         category: str = "general",
         parameters: Dict[str, str] = None):
    """Decorator to register a function as a tool"""
    return _global_registry.register(name, description, category, parameters)


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return _global_registry


def execute_tool(name: str, **kwargs) -> Any:
    """Execute a tool from the global registry"""
    return _global_registry.execute_tool(name, **kwargs)


def list_tools(category: str = None) -> List[str]:
    """List available tools"""
    return _global_registry.list_tools(category)


def get_tool_schema(name: str) -> Dict[str, Any]:
    """Get JSON schema for a tool"""
    return _global_registry.get_tool_schema(name)


# Built-in tools
@tool(
    name="write_file",
    description="Write content to a file",
    category="file_operations",
    parameters={
        "filename": "The path/name of the file to write",
        "content": "The content to write to the file"
    }
)
def write_file(filename: str, content: str) -> str:
    """Write content to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool(
    name="read_file",
    description="Read content from a file",
    category="file_operations",
    parameters={
        "filename": "The path/name of the file to read"
    }
)
def read_file(filename: str) -> str:
    """Read content from a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"File {filename} not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool(
    name="list_files",
    description="List files in a directory",
    category="file_operations",
    parameters={
        "directory": "The directory to list files from (default: current directory)"
    }
)
def list_files(directory: str = ".") -> str:
    """List files in a directory"""
    import os
    try:
        files = os.listdir(directory)
        return f"Files in {directory}:\n" + "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"


@tool(
    name="execute_python",
    description="Execute Python code and return output",
    category="code_execution",
    parameters={
        "code": "The Python code to execute"
    }
)
def execute_python(code: str) -> str:
    """Execute Python code and return output"""
    import subprocess
    import tempfile
    import sys
    import os
    
    try:
        # Create a temporary file to execute the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Execute the code
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Clean up
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return f"Output:\n{result.stdout}" if result.stdout else "Code executed successfully (no output)"
        else:
            return f"Error:\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (30s limit)"
    except Exception as e:
        return f"Error executing code: {str(e)}"


@tool(
    name="search_web",
    description="Search the web using SerpAPI",
    category="web_search",
    parameters={
        "query": "The search query",
        "num_results": "Number of results to return (default: 10)",
        "location": "Location for search (default: United States)"
    }
)
def search_web(query: str, num_results: int = 10, location: str = "United States") -> str:
    """Search the web using SerpAPI"""
    import requests
    from .config import get_config
    
    config = get_config()
    
    if not config.serpapi_key:
        return "Error: SerpAPI key not configured"
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": config.serpapi_key,
        "num": num_results,
        "location": location
    }
    
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        res = response.json()
        output = ""
        
        if "organic_results" in res:
            output += "\n--- Search Results ---\n"
            for result in res.get("organic_results", []):
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                output += f"Title: {title}\n"
                output += f"Link: {link}\n"
                output += f"Snippet: {snippet}\n"
                output += "-" * 30 + "\n"
        
        return output if output else "No results found"
        
    except Exception as e:
        return f"Error searching web: {str(e)}" 