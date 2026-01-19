"""
LLM Service - Handles ALL Ollama/LLM interactions

This service is responsible for:
- Connecting to Ollama server
- Sending prompts and receiving responses
- Managing model configuration

"""

import ollama
from typing import Dict, List
import httpx


class LLMService:
    """Service for ALL LLM/Ollama interactions"""
    
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434", timeout: int = 120):
        """
        Initialize LLM service
        
        Args:
            model: Ollama model name (e.g., 'llama3.1:8b', 'mistral', 'codellama')
            base_url: Ollama server URL
            timeout: Request timeout in seconds
        """
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        # Create client with timeout
        self.client = ollama.Client(
            host=base_url,
            timeout=httpx.Timeout(timeout=timeout, connect=10.0)
        )
        print(f"🤖 LLM Service initialized with model: {self.model} (timeout: {timeout}s)")
    
    def generate(self, prompt: str, temperature: float = 0.7, 
                 max_tokens: int = 2048) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Creativity level (0.0 - 1.0)
            max_tokens: Maximum tokens in response (reduced for speed)
            
        Returns:
            Generated text
        """
        try:
            print(f"📝 Generating with {self.model}... (this may take up to {self.timeout}s)")
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
        except httpx.TimeoutException:
            raise Exception(f"LLM generation timed out after {self.timeout}s - try a smaller model or shorter prompt")
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    def chat(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        Have a chat conversation with the LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Creativity level
            
        Returns:
            Assistant's response
        """
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                }
            )
            return response['message']['content']
        except Exception as e:
            raise Exception(f"LLM chat failed: {str(e)}")
    
    def test_connection(self) -> Dict:
        """
        Test connection to Ollama server
        
        Returns:
            Dict with connection status and available models
        """
        try:
            models = self.client.list()
            model_names = [m['name'] for m in models.get('models', [])]
            
            return {
                'connected': True,
                'models': model_names,
                'current_model': self.model,
                'model_available': any(self.model in m for m in model_names)
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'models': [],
                'current_model': self.model,
                'model_available': False
            }
    
    def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            models = self.client.list()
            return [m['name'] for m in models.get('models', [])]
        except Exception:
            return []
    
    def set_model(self, model: str):
        """Change the active model"""
        self.model = model
