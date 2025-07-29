"""
Command Line Interface for Kepler Framework
"""

import argparse
import sys
import logging
from pathlib import Path

from .core.config import load_config, Config
from .core.llm_providers import get_available_providers
from .agents.react_agent import create_react_agent
from .agents.coding_agent import create_coding_agent


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Kepler Multi-Agent Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kepler chat "What is the weather like today?"
  kepler code "Create a Python script to sort a list"
  kepler --config config.yaml chat "Hello world"
  kepler --provider anthropic chat "Explain quantum computing"
        """
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--provider", 
        type=str, 
        choices=["openai", "anthropic", "gemini"],
        help="LLM provider to use"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        help="Specific model to use"
    )
    parser.add_argument(
        "--max-iterations", 
        type=int, 
        default=50,
        help="Maximum iterations for ReAct agents"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=300,
        help="Timeout in seconds"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start a chat session")
    chat_parser.add_argument("message", nargs="?", help="Message to send")
    chat_parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    
    # Code command
    code_parser = subparsers.add_parser("code", help="Start a coding session")
    code_parser.add_argument("task", nargs="?", help="Coding task to perform")
    code_parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show framework information")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_action")
    
    config_subparsers.add_parser("show", help="Show current configuration")
    
    create_parser = config_subparsers.add_parser("create", help="Create a new configuration file")
    create_parser.add_argument("path", help="Path for the new configuration file")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    try:
        # Load configuration
        if args.config:
            config = load_config(args.config)
        else:
            config = load_config()
        
        # Override config with CLI arguments
        if args.provider:
            # Update provider-specific settings
            pass
        if args.model:
            if args.provider == "openai":
                config.default_openai_model = args.model
            elif args.provider == "anthropic":
                config.default_anthropic_model = args.model
            elif args.provider == "gemini":
                config.default_gemini_model = args.model
        
        config.max_iterations = args.max_iterations
        config.timeout_seconds = args.timeout
        
        # Execute command
        if args.command == "info":
            show_info(config)
        elif args.command == "config":
            handle_config_command(args, config)
        elif args.command == "chat":
            handle_chat_command(args, config)
        elif args.command == "code":
            handle_code_command(args, config)
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def show_info(config: Config):
    """Show framework information"""
    print("Kepler Multi-Agent Framework")
    print("=" * 40)
    print(f"Version: 0.1.0")
    print(f"Available providers: {', '.join(get_available_providers())}")
    print(f"Max iterations: {config.max_iterations}")
    print(f"Timeout: {config.timeout_seconds}s")
    print()
    
    # Show tool information
    from .core.tools import get_tool_registry
    registry = get_tool_registry()
    categories = registry.get_categories()
    
    print("Available Tools:")
    for category in categories:
        tools = registry.list_tools(category)
        print(f"  {category}: {', '.join(tools)}")


def handle_config_command(args, config: Config):
    """Handle configuration commands"""
    if args.config_action == "show":
        print("Current Configuration:")
        print("=" * 30)
        print(f"OpenAI API Key: {'Set' if config.openai_api_key else 'Not set'}")
        print(f"Anthropic API Key: {'Set' if config.anthropic_api_key else 'Not set'}")
        print(f"Gemini API Key: {'Set' if config.gemini_api_key else 'Not set'}")
        print(f"SerpAPI Key: {'Set' if config.serpapi_key else 'Not set'}")
        print(f"Max Iterations: {config.max_iterations}")
        print(f"Timeout: {config.timeout_seconds}s")
        
    elif args.config_action == "create":
        # Create a sample configuration file
        sample_config = {
            "openai_api_key": "your-openai-api-key-here",
            "anthropic_api_key": "your-anthropic-api-key-here", 
            "gemini_api_key": "your-gemini-api-key-here",
            "serpapi_key": "your-serpapi-key-here",
            "max_iterations": 50,
            "timeout_seconds": 300,
            "log_level": "INFO"
        }
        
        config_path = Path(args.path)
        config.save_to_file(str(config_path))
        print(f"Created configuration file: {config_path}")
        print("Please edit the file to add your API keys.")


def handle_chat_command(args, config: Config):
    """Handle chat command"""
    provider = getattr(args, 'provider', None) or 'openai'
    
    # Create agent
    agent = create_react_agent(
        name="chat_agent",
        provider=provider,
        max_iterations=config.max_iterations,
        timeout_seconds=config.timeout_seconds
    )
    
    if args.interactive or not args.message:
        # Interactive mode
        print("Kepler Chat Agent (type 'quit' to exit)")
        print("-" * 40)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                print("\nAgent: ", end="", flush=True)
                response = agent.process(user_input)
                
                if response.success:
                    print(response.content)
                else:
                    print(f"Error: {response.error}")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
    else:
        # Single message mode
        response = agent.process(args.message)
        if response.success:
            print(response.content)
        else:
            print(f"Error: {response.error}")
            sys.exit(1)


def handle_code_command(args, config: Config):
    """Handle code command"""
    provider = getattr(args, 'provider', None) or 'openai'
    
    # Create coding agent
    agent = create_coding_agent(
        name="coding_agent",
        provider=provider,
        max_iterations=config.max_iterations,
        timeout_seconds=config.timeout_seconds
    )
    
    if args.interactive or not args.task:
        # Interactive mode
        print("Kepler Coding Agent (type 'quit' to exit)")
        print("-" * 40)
        
        while True:
            try:
                user_input = input("\nCoding Task: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                print("\nAgent: ", end="", flush=True)
                response = agent.process(user_input)
                
                if response.success:
                    print(response.content)
                    if hasattr(agent, 'get_steps_summary'):
                        print("\n" + "="*50)
                        print(agent.get_steps_summary())
                else:
                    print(f"Error: {response.error}")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
    else:
        # Single task mode
        response = agent.process(args.task)
        if response.success:
            print(response.content)
            if hasattr(agent, 'get_steps_summary'):
                print("\n" + "="*50)
                print(agent.get_steps_summary())
        else:
            print(f"Error: {response.error}")
            sys.exit(1)


if __name__ == "__main__":
    main() 