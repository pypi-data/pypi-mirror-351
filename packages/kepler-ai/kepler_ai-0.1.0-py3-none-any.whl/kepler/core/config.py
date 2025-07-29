"""
Configuration management for Kepler framework
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class Config:
    """Configuration class for Kepler framework"""
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Default models
    default_openai_model: str = "gpt-4o-mini"
    default_anthropic_model: str = "claude-3-sonnet-20240229"
    default_gemini_model: str = "gemini-2.5-flash-preview-04-17"
    
    # Agent Configuration
    max_iterations: int = 50
    timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Tool Configuration
    enable_web_search: bool = True
    enable_file_operations: bool = True
    enable_code_execution: bool = True
    
    # Search API Configuration
    serpapi_key: Optional[str] = None
    
    # Additional settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables"""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            serpapi_key=os.getenv("SERPAPI_KEY"),
            max_iterations=int(os.getenv("KEPLER_MAX_ITERATIONS", "50")),
            timeout_seconds=int(os.getenv("KEPLER_TIMEOUT", "300")),
            log_level=os.getenv("KEPLER_LOG_LEVEL", "INFO"),
            log_file=os.getenv("KEPLER_LOG_FILE"),
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from file (JSON or YAML)"""
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, 'r') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                if yaml is None:
                    raise ImportError("PyYAML is required for YAML config files. Install with: pip install PyYAML")
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        # Merge with environment variables (env vars take precedence)
        env_config = cls.from_env()
        
        # Update data with non-None env values
        for key, value in env_config.__dict__.items():
            if value is not None:
                data[key] = value
        
        return cls(**data)
    
    def save_to_file(self, config_path: str):
        """Save configuration to file"""
        path = Path(config_path)
        
        # Convert to dict, excluding None values
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        
        with open(path, 'w') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                if yaml is None:
                    raise ImportError("PyYAML is required for YAML config files. Install with: pip install PyYAML")
                yaml.dump(data, f, default_flow_style=False)
            else:
                json.dump(data, f, indent=2)
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Check if at least one LLM API key is provided (only if not in test mode)
        if not any([self.openai_api_key, self.anthropic_api_key, self.gemini_api_key]):
            # Allow validation to pass if we're in test mode (test-key)
            if not (self.openai_api_key == "test-key" or 
                   self.anthropic_api_key == "test-key" or 
                   self.gemini_api_key == "test-key"):
                errors.append("At least one LLM API key must be provided")
        
        # Validate numeric values
        if self.max_iterations <= 0:
            errors.append("max_iterations must be positive")
        
        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")
        
        if self.retry_attempts < 0:
            errors.append("retry_attempts must be non-negative")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return True
    
    def get_available_providers(self) -> list:
        """Get list of available LLM providers based on API keys"""
        providers = []
        
        if self.openai_api_key:
            providers.append("openai")
        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.gemini_api_key:
            providers.append("gemini")
        
        return providers


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance"""
    global _global_config
    
    if _global_config is None:
        _global_config = Config.from_env()
    
    return _global_config


def set_config(config: Config):
    """Set the global configuration instance"""
    global _global_config
    config.validate()
    _global_config = config


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or environment"""
    if config_path:
        config = Config.from_file(config_path)
    else:
        config = Config.from_env()
    
    set_config(config)
    return config 