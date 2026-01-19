"""
LLM Service - Handles ALL LLM interactions (Ollama, OpenAI, etc.)

This service provides a unified interface for multiple LLM providers:
- Ollama (local models like llama3.1:8b, mistral, codellama)
- OpenAI (GPT-3.5, GPT-4, etc.)

Configuration via environment variables:
- LLM_PROVIDER: 'ollama' (default) or 'openai'
- OLLAMA_MODEL: Model name for Ollama
- OPENAI_API_KEY: API key for OpenAI
- OPENAI_MODEL: Model name for OpenAI (e.g., 'gpt-4', 'gpt-3.5-turbo')
"""

import os
from typing import Dict, List, Optional
import httpx


class LLMService:
    """Unified service for ALL LLM interactions across multiple providers"""
    
    def __init__(self, 
                 provider: Optional[str] = None,
                 model: Optional[str] = None,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 timeout: int = 120):
        """
        Initialize LLM service with configurable provider
        
        Args:
            provider: 'ollama' or 'openai' (default: from env or 'ollama')
            model: Model name (default: from env or provider-specific default)
            api_key: API key for OpenAI (default: from env)
            base_url: Base URL for provider (default: provider-specific)
            timeout: Request timeout in seconds
        """
        # Determine provider
        self.provider = provider or os.getenv('LLM_PROVIDER', 'ollama').lower()
        self.timeout = timeout
        
        # Initialize based on provider
        if self.provider == 'openai':
            self._init_openai(model, api_key)
        else:  # Default to Ollama
            self._init_ollama(model, base_url)
        
        print(f"🤖 LLM Service initialized: {self.provider} - {self.model} (timeout: {timeout}s)")
    
    def _init_ollama(self, model: Optional[str], base_url: Optional[str]):
        """Initialize Ollama provider"""
        import ollama
        
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        # Create Ollama client with timeout
        self.client = ollama.Client(
            host=self.base_url,
            timeout=httpx.Timeout(timeout=self.timeout, connect=10.0)
        )
    
    def _init_openai(self, model: Optional[str], api_key: Optional[str]):
        """Initialize OpenAI provider"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )
        
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4-nano')
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(
            api_key=api_key,
            timeout=self.timeout
        )
    
    def generate(self, prompt: str, temperature: float = 0.7, 
                 max_tokens: int = 2048) -> str:
        """
        Generate text from a prompt (unified interface)
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Creativity level (0.0 - 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text
        """
        print(f"📝 Generating with {self.provider}/{self.model}... (max {self.timeout}s)")
        
        try:
            if self.provider == 'openai':
                return self._generate_openai(prompt, temperature, max_tokens)
            else:  # ollama
                return self._generate_ollama(prompt, temperature, max_tokens)
        except httpx.TimeoutException:
            raise Exception(f"LLM generation timed out after {self.timeout}s")
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    def _generate_ollama(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate using Ollama"""
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options={
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": max_tokens,
            }
        )
        print(f"✅ Generation complete!")
        return response['response']
    
    def _generate_openai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        print(f"✅ Generation complete!")
        return response.choices[0].message.content
    
    def chat(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        Have a chat conversation with the LLM (unified interface)
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Creativity level
            
        Returns:
            Assistant's response
        """
        try:
            if self.provider == 'openai':
                return self._chat_openai(messages, temperature)
            else:  # ollama
                return self._chat_ollama(messages, temperature)
        except Exception as e:
            raise Exception(f"LLM chat failed: {str(e)}")
    
    def _chat_ollama(self, messages: List[Dict], temperature: float) -> str:
        """Chat using Ollama"""
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": temperature,
            }
        )
        return response['message']['content']
    
    def _chat_openai(self, messages: List[Dict], temperature: float) -> str:
        """Chat using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
        return response.choices[0].message.content
    
    def test_connection(self) -> Dict:
        """
        Test connection to LLM provider
        
        Returns:
            Dict with connection status and available models
        """
        try:
            if self.provider == 'openai':
                return self._test_openai()
            else:  # ollama
                return self._test_ollama()
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'provider': self.provider,
                'model': self.model,
                'model_available': False
            }
    
    def _test_ollama(self) -> Dict:
        """Test Ollama connection"""
        models = self.client.list()
        model_names = [m['name'] for m in models.get('models', [])]
        
        return {
            'connected': True,
            'provider': 'ollama',
            'models': model_names,
            'current_model': self.model,
            'model_available': any(self.model in m for m in model_names)
        }
    
    def _test_openai(self) -> Dict:
        """Test OpenAI connection"""
        # Try a minimal API call to verify connection
        self.client.models.list()
        
        return {
            'connected': True,
            'provider': 'openai',
            'current_model': self.model,
            'model_available': True  # If we got here, API key works
        }
    
    def list_models(self) -> List[str]:
        """List available models for current provider"""
        try:
            if self.provider == 'openai':
                models = self.client.models.list()
                return [m.id for m in models.data]
            else:  # ollama
                models = self.client.list()
                return [m['name'] for m in models.get('models', [])]
        except Exception:
            return []
    
    def set_model(self, model: str):
        """Change the active model"""
        self.model = model
    
    def get_info(self) -> Dict:
        """Get current LLM service configuration"""
        return {
            'provider': self.provider,
            'model': self.model,
            'timeout': self.timeout,
            'base_url': getattr(self, 'base_url', None)
        }
