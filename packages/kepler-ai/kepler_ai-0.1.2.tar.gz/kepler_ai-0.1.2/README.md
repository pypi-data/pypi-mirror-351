# Kepler Multi-Agent Framework

A powerful, flexible framework for building AI agents with multiple LLM support, function calling, and ReAct reasoning capabilities.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/kepler-ai.svg)](https://badge.fury.io/py/kepler-ai)

## Features

- **Multiple LLM Support**: OpenAI GPT, Anthropic Claude, Google Gemini
- **ReAct Reasoning**: Advanced reasoning and acting capabilities
- **Easy Function Calling**: Decorator-based tool registration
- **Agent Composition**: Create complex multi-agent systems
- **Robust Error Handling**: Comprehensive error handling and retry mechanisms
- **Flexible Configuration**: Environment variables, config files, or programmatic setup
- **CLI Interface**: Command-line interface for quick interactions
- **Type Safety**: Full type hints and validation with Pydantic

## Installation

### Basic Installation

```bash
pip install kepler-ai
```

### With LLM Providers

```bash
# Install with OpenAI support
pip install kepler-ai[openai]

# Install with Anthropic support  
pip install kepler-ai[anthropic]

# Install with Google Gemini support
pip install kepler-ai[gemini]

# Install with all providers
pip install kepler-ai[all]
```

### Development Installation

```bash
git clone https://github.com/kepler-team/kepler-framework.git
cd kepler-framework
pip install -e .[dev]
```

## Quick Setup

### 1. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GEMINI_API_KEY="your-gemini-api-key"
export SERPAPI_KEY="your-serpapi-key"  # Optional, for web search
```

### 2. Or Create a Configuration File

```bash
kepler config create config.yaml
```

Edit the generated `config.yaml`:

```yaml
openai_api_key: "your-openai-api-key"
anthropic_api_key: "your-anthropic-api-key"
gemini_api_key: "your-gemini-api-key"
serpapi_key: "your-serpapi-key"
max_iterations: 50
timeout_seconds: 300
log_level: "INFO"
```

## Quick Start

### Command Line Interface

```bash
# Chat with an agent
kepler chat "What is the weather like today?"

# Interactive chat mode
kepler chat --interactive

# Coding tasks
kepler code "Create a Python script to sort a list"

# Use specific provider
kepler --provider anthropic chat "Explain quantum computing"

# Show framework info
kepler info
```

### Python API

#### Simple Agent

```python
import kepler

# Create a simple agent
agent = kepler.create_agent(
    name="my_agent",
    provider="openai",
    system_prompt="You are a helpful assistant."
)

# Process a message
response = agent.process("Hello, how are you?")
print(response.content)
```

#### ReAct Agent with Tools

```python
import kepler

# Create a ReAct agent with tools
agent = kepler.create_react_agent(
    name="research_agent",
    provider="openai",
    tools=["search_web", "write_file", "read_file"]
)

# Process a complex task
response = agent.process("Research the latest developments in AI and write a summary")
print(response.content)

# View the reasoning steps
if hasattr(agent, 'get_steps_summary'):
    print(agent.get_steps_summary())
```

#### Coding Agent

```python
import kepler

# Create a specialized coding agent
agent = kepler.create_coding_agent(
    name="coder",
    provider="anthropic"
)

# Give it a coding task
response = agent.process("Create a REST API using FastAPI with user authentication")
print(response.content)
```

### Function-Based Agents

```python
import kepler

@kepler.agent_function(
    name="math_tutor",
    provider="openai",
    system_prompt="You are a math tutor. Help students understand mathematical concepts.",
    tools=["execute_python"]
)
def math_tutor(question: str):
    """A math tutoring agent"""
    pass

# Use the agent
response = math_tutor("Explain calculus derivatives with examples")
print(response.content)
```

### Custom Tools

```python
import kepler

@kepler.tool(
    name="get_weather",
    description="Get weather information for a location",
    category="weather",
    parameters={
        "location": "The city or location to get weather for",
        "units": "Temperature units (celsius or fahrenheit)"
    }
)
def get_weather(location: str, units: str = "celsius") -> str:
    """Get weather information"""
    # Your weather API logic here
    return f"The weather in {location} is sunny, 25°{units[0].upper()}"

# Create agent with custom tool
agent = kepler.create_tool_agent(
    name="weather_agent",
    tools=["get_weather"]
)

response = agent.process("What's the weather like in Paris?")
print(response.content)
```

## Architecture

### Core Components

- **LLM Providers**: Unified interface for different AI models
- **Agents**: Base classes for different agent types
- **Tools**: Function calling system with automatic registration
- **Configuration**: Flexible configuration management
- **CLI**: Command-line interface for easy interaction

### Agent Types

1. **SimpleAgent**: Basic conversational agent
2. **ToolAgent**: Agent with function calling capabilities  
3. **ReActAgent**: Reasoning and acting agent
4. **CodingAgent**: Specialized agent for coding tasks

## Advanced Usage

### Multiple LLM Providers

```python
import kepler

# Configure multiple providers
config = kepler.Config(
    openai_api_key="your-openai-key",
    anthropic_api_key="your-anthropic-key",
    gemini_api_key="your-gemini-key"
)
kepler.set_config(config)

# Create agents with different providers
openai_agent = kepler.create_agent("openai_agent", provider="openai")
claude_agent = kepler.create_agent("claude_agent", provider="anthropic") 
gemini_agent = kepler.create_agent("gemini_agent", provider="gemini")
```

### Agent Composition

```python
import kepler

# Create specialized agents
researcher = kepler.create_react_agent(
    name="researcher",
    tools=["search_web", "read_file"]
)

writer = kepler.create_agent(
    name="writer", 
    system_prompt="You are a technical writer. Create clear, well-structured content."
)

coder = kepler.create_coding_agent(name="coder")

# Orchestrate multiple agents
def research_and_code(topic: str):
    # Research phase
    research_result = researcher.process(f"Research {topic} and gather information")
    
    # Writing phase  
    article = writer.process(f"Write an article about: {research_result.content}")
    
    # Coding phase
    code_result = coder.process(f"Create code examples for: {topic}")
    
    return {
        "research": research_result.content,
        "article": article.content, 
        "code": code_result.content
    }

result = research_and_code("machine learning algorithms")
```

### Error Handling and Retries

```python
import kepler

# Configure retry behavior
config = kepler.Config(
    retry_attempts=3,
    retry_delay=1.0,
    timeout_seconds=300
)

agent = kepler.create_agent(
    name="robust_agent",
    max_iterations=10,
    timeout_seconds=60
)

try:
    response = agent.process("Complex task that might fail")
    if response.success:
        print(response.content)
    else:
        print(f"Agent failed: {response.error}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

### Environment Variables

```bash
# LLM API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key  
GEMINI_API_KEY=your-gemini-api-key

# Optional APIs
SERPAPI_KEY=your-serpapi-key

# Framework Settings
KEPLER_MAX_ITERATIONS=50
KEPLER_TIMEOUT=300
KEPLER_LOG_LEVEL=INFO
KEPLER_LOG_FILE=kepler.log
```

### Configuration File

```yaml
# config.yaml
openai_api_key: "your-openai-api-key"
anthropic_api_key: "your-anthropic-api-key"
gemini_api_key: "your-gemini-api-key"
serpapi_key: "your-serpapi-key"

# Default models
default_openai_model: "gpt-4"
default_anthropic_model: "claude-3-sonnet-20240229"
default_gemini_model: "gemini-2.5-flash-preview-04-17"

# Agent settings
max_iterations: 50
timeout_seconds: 300
retry_attempts: 3
retry_delay: 1.0

# Logging
log_level: "INFO"
log_file: "kepler.log"

# Tool settings
enable_web_search: true
enable_file_operations: true
enable_code_execution: true
```

## Built-in Tools

### File Operations
- `write_file`: Write content to files
- `read_file`: Read file contents
- `list_files`: List directory contents

### Code Execution
- `execute_python`: Execute Python code safely

### Web Search
- `search_web`: Search the web using SerpAPI

### Custom Tools
Create your own tools using the `@tool` decorator:

```python
@kepler.tool(
    name="custom_tool",
    description="Description of what the tool does",
    category="custom",
    parameters={
        "param1": "Description of parameter 1",
        "param2": "Description of parameter 2"
    }
)
def custom_tool(param1: str, param2: int = 10) -> str:
    """Custom tool implementation"""
    return f"Processed {param1} with {param2}"
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=kepler

# Run specific test categories
pytest -m unit
pytest -m integration
```

## Examples

Check out the `examples/` directory for more comprehensive examples:

- `basic_usage.py`: Simple agent interactions
- `react_agent.py`: ReAct reasoning examples
- `custom_tools.py`: Creating custom tools
- `multi_agent.py`: Multi-agent orchestration
- `coding_tasks.py`: Coding agent examples

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/sandeep-chakraborty/kepler/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sandeep-chakraborty/kepler/discussions)

## Roadmap

- [ ] Async/await support
- [ ] More LLM providers (Cohere, Hugging Face)
- [ ] Agent memory and persistence
- [ ] Web UI for agent management
- [ ] Plugin system
- [ ] Performance optimizations
- [ ] Advanced agent orchestration patterns

---

**Made with care by Sandeep.** 