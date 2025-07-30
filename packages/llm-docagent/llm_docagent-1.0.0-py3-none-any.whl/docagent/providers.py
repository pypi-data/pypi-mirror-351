import os
import time
import requests
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from dotenv import load_dotenv
from dataclasses import dataclass
load_dotenv()
class ProviderType(Enum):
    """Supported LLM provider types"""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface" 
    OLLAMA = "ollama"
    GROQ="groq"
    FALLBACK = "fallback"

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, **kwargs):
        self.config = kwargs
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # seconds between requests
    
    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        """Generate text using the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured"""
        pass
    
    def _rate_limit(self):
        """Simple rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider with robust error handling"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        self.rate_limit_delay = 1.0  # OpenAI rate limiting
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return bool(self.api_key)
    
    def generate_text(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        """Generate text using OpenAI API"""
        if not self.is_available():
            raise ValueError("OpenAI API key not configured")
        
        self._rate_limit()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a technical documentation expert. Generate clear, comprehensive documentation."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            
            elif response.status_code == 429:
                print("⚠️  OpenAI rate limit hit, waiting...")
                time.sleep(5)
                return self.generate_text(prompt, max_tokens, temperature)
            
            else:
                error_detail = response.json().get("error", {}).get("message", "Unknown error")
                raise Exception(f"OpenAI API error {response.status_code}: {error_detail}")
                
        except requests.RequestException as e:
            raise Exception(f"OpenAI API request failed: {str(e)}")

class HuggingFaceProvider(BaseLLMProvider):
    """Hugging Face Inference API provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
        self.model = model
        self.base_url = "https://api-inference.huggingface.co/models"
        self.rate_limit_delay = 2.0  # HF has stricter rate limits
    
    def is_available(self) -> bool:
        """Check if Hugging Face is available"""
        return bool(self.api_key)
    
    def generate_text(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        """Generate text using Hugging Face Inference API"""
        if not self.is_available():
            raise ValueError("Hugging Face API key not configured")
        
        self._rate_limit()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Format prompt for better documentation generation
        formatted_prompt = f"""
Generate comprehensive technical documentation for the following codebase analysis:

{prompt}

Please provide:
1. Clear project overview
2. Architecture explanation  
3. Installation instructions
4. Usage examples
5. Key components description

Documentation:"""
        
        data = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "do_sample": True,
                "return_full_text": False
            },
            "options": {
                "wait_for_model": True,
                "use_cache": False
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=headers,
                json=data,
                timeout=120  # HF can be slower
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                elif isinstance(result, dict):
                    return result.get("generated_text", "").strip()
                else:
                    return str(result).strip()
            
            elif response.status_code == 503:
                print(" Hugging Face model loading, retrying...")
                time.sleep(10)
                return self.generate_text(prompt, max_tokens, temperature)
            
            else:
                error_msg = response.json().get("error", "Unknown error")
                raise Exception(f"Hugging Face API error {response.status_code}: {error_msg}")
                
        except requests.RequestException as e:
            raise Exception(f"Hugging Face API request failed: {str(e)}")

class OllamaProvider(BaseLLMProvider):
    """Local Ollama provider"""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.base_url = base_url
        self.rate_limit_delay = 0.5  # Local, so faster
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_text(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        """Generate text using Ollama"""
        if not self.is_available():
            raise ValueError("Ollama not available. Make sure it's running on localhost:11434")
        
        self._rate_limit()
        
        # Enhanced prompt for better documentation
        system_prompt = """You are a technical writer creating comprehensive documentation. 
Generate clear, well-structured documentation with proper sections and examples."""
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        data = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "top_k": 40,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=180  # Local models can be slow
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                raise Exception(f"Ollama API error {response.status_code}: {response.text}")
                
        except requests.RequestException as e:
            raise Exception(f"Ollama request failed: {str(e)}")
class GroqProvider(BaseLLMProvider):
    """Groq AI provider with fast inference"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama3-8b-8192", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
        self.rate_limit_delay = 0.5  # Groq is fast, so shorter delay
    
    def is_available(self) -> bool:
        """Check if Groq is available"""
        return bool(self.api_key)
    
    def generate_text(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        """Generate text using Groq API"""
        if not self.is_available():
            raise ValueError("Groq API key not configured")
        
        self._rate_limit()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a technical documentation expert. Generate clear, comprehensive documentation."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30  # Groq is fast
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            
            elif response.status_code == 429:
                print("Groq rate limit hit, waiting...")
                time.sleep(2)
                return self.generate_text(prompt, max_tokens, temperature)
            
            else:
                error_detail = response.json().get("error", {}).get("message", "Unknown error")
                raise Exception(f"Groq API error {response.status_code}: {error_detail}")
                
        except requests.RequestException as e:
            raise Exception(f"Groq API request failed: {str(e)}")

class FallbackProvider(BaseLLMProvider):
    """Fallback provider when no LLM is available"""
    
    def is_available(self) -> bool:
        return True
    
    def generate_text(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        """Generate basic documentation template"""
        return """# Project Documentation

## Overview
This project has been analyzed automatically by DocAgent. The codebase contains multiple files and components working together.

## Architecture
The project structure includes various source files, configuration files, and documentation. Each component serves a specific purpose in the overall system.

## Installation
1. Clone or download the project
2. Install required dependencies
3. Configure environment variables if needed
4. Run the main application

## Usage
Refer to the source code files for specific usage instructions. Key entry points and main functions are typically found in files named `main`, `app`, `index`, or similar.

## Components
The codebase has been organized into logical components. Check individual files for detailed implementation.

## Contributing
Please follow the existing code style and add appropriate tests for new features.

---
*Generated by DocAgent - Configure an LLM provider for enhanced AI-generated documentation*
"""

class LLMManager:
    """Manages multiple LLM providers with fallback"""
    
    def __init__(self, preferred_provider: str = "auto"):
        self.providers = {}
        self.preferred_provider = preferred_provider
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers"""
        # Initialize providers
        self.providers = {
            ProviderType.OPENAI: OpenAIProvider(),
            ProviderType.HUGGINGFACE: HuggingFaceProvider(),
            ProviderType.GROQ: GroqProvider(),
            ProviderType.OLLAMA: OllamaProvider(),
            ProviderType.FALLBACK: FallbackProvider()
            
        }
    
    def get_best_provider(self) -> BaseLLMProvider:
        """Get the best available provider"""
        if self.preferred_provider != "auto":
            try:
                provider_type = ProviderType(self.preferred_provider)
                provider = self.providers[provider_type]
                if provider.is_available():
                    return provider
            except (ValueError, KeyError):
                print(f"Invalid provider '{self.preferred_provider}', using auto-detection")
        
        # Auto-detect best provider
        priority_order = [ProviderType.GROQ,ProviderType.OPENAI, ProviderType.HUGGINGFACE, ProviderType.OLLAMA, ProviderType.FALLBACK]
        
        for provider_type in priority_order:
            provider = self.providers[provider_type]
            if provider.is_available():
                provider_name = provider_type.value
                if provider_type != ProviderType.FALLBACK:
                    print(f"Using {provider_name} for documentation generation")
                else:
                    print(" No LLM providers available, using fallback templates")
                return provider
        
        # Should never reach here, but safety fallback
        return self.providers[ProviderType.FALLBACK]
