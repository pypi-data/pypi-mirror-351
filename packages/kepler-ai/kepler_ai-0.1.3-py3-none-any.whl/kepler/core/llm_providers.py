"""
LLM Provider abstraction for multiple AI model support
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import logging

# Import LLM clients
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

from .config import get_config


logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Standardized response from LLM providers"""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = get_config()
        self.client = None
        self._initialize_client(**kwargs)
    
    @abstractmethod
    def _initialize_client(self, **kwargs):
        """Initialize the LLM client"""
        pass
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response from messages"""
        pass
    
    @abstractmethod
    def generate_structured(self, messages: List[Dict[str, str]], schema: Dict[str, Any], **kwargs) -> LLMResponse:
        """Generate structured response using JSON schema"""
        pass
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff"""
        for attempt in range(self.config.retry_attempts + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.config.retry_attempts:
                    raise e
                
                wait_time = self.config.retry_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def _initialize_client(self, **kwargs):
        if OpenAI is None:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.client = OpenAI(api_key=self.api_key, **kwargs)
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using OpenAI API"""
        def _generate():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.1),
                max_tokens=kwargs.get('max_tokens'),
                **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
        
        return self._retry_with_backoff(_generate)
    
    def generate_structured(self, messages: List[Dict[str, str]], schema: Dict[str, Any], **kwargs) -> LLMResponse:
        """Generate structured response using OpenAI's structured output"""
        def _generate():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.1),
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema.get("name", "response"),
                        "schema": schema
                    }
                },
                **{k: v for k, v in kwargs.items() if k not in ['temperature']}
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
        
        return self._retry_with_backoff(_generate)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def _initialize_client(self, **kwargs):
        if anthropic is None:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=self.api_key, **kwargs)
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using Anthropic API"""
        def _generate():
            # Convert messages format for Anthropic
            system_message = None
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = self.client.messages.create(
                model=self.model,
                messages=anthropic_messages,
                system=system_message,
                max_tokens=kwargs.get('max_tokens', 4000),
                temperature=kwargs.get('temperature', 0.1),
                **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=self.model,
                provider="anthropic",
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                metadata={"stop_reason": response.stop_reason}
            )
        
        return self._retry_with_backoff(_generate)
    
    def generate_structured(self, messages: List[Dict[str, str]], schema: Dict[str, Any], **kwargs) -> LLMResponse:
        """Generate structured response (Anthropic doesn't have native structured output, so we use prompt engineering)"""
        # Add JSON schema instruction to the last message
        schema_prompt = f"\n\nPlease respond with valid JSON that matches this schema:\n{schema}\n\nResponse:"
        
        if messages:
            messages[-1]["content"] += schema_prompt
        
        return self.generate(messages, **kwargs)


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    
    def _initialize_client(self, **kwargs):
        if genai is None:
            raise ImportError("Google GenAI package not installed. Run: pip install google-genai")
        
        self.client = genai.Client(api_key=self.api_key, **kwargs)
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response using Gemini API"""
        def _generate():
            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                if msg["role"] == "system":
                    # Gemini doesn't have system role, prepend to first user message
                    if contents and contents[0].role == "user":
                        contents[0].parts[0].text = f"{msg['content']}\n\n{contents[0].parts[0].text}"
                    else:
                        contents.insert(0, types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=msg["content"])]
                        ))
                else:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    ))
            
            config = types.GenerateContentConfig(
                temperature=kwargs.get('temperature', 0.1),
                max_output_tokens=kwargs.get('max_tokens'),
                response_mime_type="text/plain"
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )
            
            return LLMResponse(
                content=response.text,
                model=self.model,
                provider="gemini",
                usage=None,  # Gemini doesn't provide usage info in the same format
                metadata={"finish_reason": getattr(response, 'finish_reason', None)}
            )
        
        return self._retry_with_backoff(_generate)
    
    def generate_structured(self, messages: List[Dict[str, str]], schema: Dict[str, Any], **kwargs) -> LLMResponse:
        """Generate structured response using Gemini"""
        # Add JSON schema instruction
        schema_prompt = f"\n\nPlease respond with valid JSON that matches this schema:\n{schema}\n\nResponse:"
        
        if messages:
            messages[-1]["content"] += schema_prompt
        
        # Set response format to JSON
        kwargs["response_mime_type"] = "application/json"
        
        return self.generate(messages, **kwargs)


class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, model: str = None, api_key: str = None, **kwargs) -> LLMProvider:
        """Create an LLM provider instance"""
        config = get_config()
        
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {list(cls._providers.keys())}")
        
        # Get API key from config if not provided
        if api_key is None:
            if provider_name == "openai":
                api_key = config.openai_api_key
                model = model or config.default_openai_model
            elif provider_name == "anthropic":
                api_key = config.anthropic_api_key
                model = model or config.default_anthropic_model
            elif provider_name == "gemini":
                api_key = config.gemini_api_key
                model = model or config.default_gemini_model
        
        if not api_key:
            raise ValueError(f"No API key found for provider: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(api_key=api_key, model=model, **kwargs)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Register a custom provider"""
        cls._providers[name] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available providers"""
        config = get_config()
        available = []
        
        for provider in cls._providers.keys():
            if provider == "openai" and config.openai_api_key:
                available.append(provider)
            elif provider == "anthropic" and config.anthropic_api_key:
                available.append(provider)
            elif provider == "gemini" and config.gemini_api_key:
                available.append(provider)
        
        return available


# Convenience functions
def create_provider(provider_name: str, model: str = None, **kwargs) -> LLMProvider:
    """Create an LLM provider"""
    return LLMProviderFactory.create_provider(provider_name, model, **kwargs)


def get_available_providers() -> List[str]:
    """Get available providers based on configuration"""
    return LLMProviderFactory.get_available_providers() 