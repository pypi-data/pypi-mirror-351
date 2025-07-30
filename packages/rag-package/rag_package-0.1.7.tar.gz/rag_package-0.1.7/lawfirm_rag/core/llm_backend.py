"""
LLM Backend Abstraction Layer for LawFirm-RAG.

Provides a unified interface for different LLM backends including Ollama and llama-cpp-python,
allowing runtime switching between implementations using the Strategy pattern.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union, Iterator
from pathlib import Path
import os
import json

from .ollama_client import OllamaClient, OllamaConnectionError, OllamaModelError
from ..utils.config import get_model_name

logger = logging.getLogger(__name__)


class LLMBackendError(Exception):
    """Base exception for LLM backend errors."""
    pass


class BackendNotAvailableError(LLMBackendError):
    """Raised when a backend is not available or properly configured."""
    pass


class ModelNotLoadedError(LLMBackendError):
    """Raised when attempting to use a model that isn't loaded."""
    pass


class LLMBackend(ABC):
    """Abstract base class for LLM backends."""
    
    def __init__(self, **kwargs):
        """Initialize the backend with configuration parameters."""
        self.config = kwargs
        self.is_initialized = False
        self.current_model = None
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the backend and verify it's ready for use.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def generate(self, 
                prompt: str, 
                model: Optional[str] = None,
                max_tokens: int = 1000,
                temperature: float = 0.7,
                stream: bool = False,
                **kwargs) -> Union[str, Iterator[str]]:
        """Generate text completion.
        
        Args:
            prompt: Input prompt for text generation
            model: Model name to use (optional, uses default if not specified)
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text or iterator for streaming responses
        """
        pass
    
    @abstractmethod
    def chat(self, 
             messages: List[Dict[str, str]], 
             model: Optional[str] = None,
             max_tokens: int = 1000,
             temperature: float = 0.7,
             stream: bool = False,
             **kwargs) -> Union[str, Iterator[str]]:
        """Generate chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use (optional, uses default if not specified)
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            **kwargs: Additional chat parameters
            
        Returns:
            Generated response or iterator for streaming responses
        """
        pass
    
    @abstractmethod
    def embed(self, 
              input_text: Union[str, List[str]], 
              model: Optional[str] = None) -> Union[List[float], List[List[float]]]:
        """Generate embeddings for input text.
        
        Args:
            input_text: Text or list of texts to embed
            model: Embedding model name (optional, uses default if not specified)
            
        Returns:
            Embedding vector(s)
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models.
        
        Returns:
            List of model names
        """
        pass
    
    @abstractmethod
    def is_model_available(self, model: str) -> bool:
        """Check if a specific model is available.
        
        Args:
            model: Model name to check
            
        Returns:
            True if model is available, False otherwise
        """
        pass
    
    @abstractmethod
    def load_model(self, model: str) -> bool:
        """Load a specific model.
        
        Args:
            model: Model name to load
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def unload_model(self) -> bool:
        """Unload the currently loaded model.
        
        Returns:
            True if model unloaded successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the backend is available and ready for use.
        
        Returns:
            True if backend is available, False otherwise
        """
        pass
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the backend.
        
        Returns:
            Dictionary with backend information
        """
        return {
            "backend_type": self.__class__.__name__,
            "is_initialized": self.is_initialized,
            "current_model": self.current_model,
            "config": self.config
        }


class OllamaBackend(LLMBackend):
    """Ollama backend implementation."""
    
    def __init__(self, 
                 base_url: Optional[str] = None,
                 default_model: Optional[str] = None,
                 default_embed_model: Optional[str] = None,
                 **kwargs):
        """Initialize Ollama backend.
        
        Args:
            base_url: Ollama server URL
            default_model: Default model for text generation (if None, uses config)
            default_embed_model: Default model for embeddings (if None, uses config)
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self.base_url = base_url
        
        # Use configured models if not explicitly provided
        self.default_model = default_model or get_model_name("chat")
        self.default_embed_model = default_embed_model or get_model_name("embeddings")
        
        self.client = None
    
    def initialize(self) -> bool:
        """Initialize the Ollama client and verify connection."""
        try:
            self.client = OllamaClient(base_url=self.base_url, **self.config)
            
            # Test connection
            if self.client.is_available():
                self.is_initialized = True
                logger.info("Ollama backend initialized successfully")
                return True
            else:
                logger.error("Ollama server is not available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Ollama backend: {e}")
            return False
    
    def generate(self, 
                prompt: str, 
                model: Optional[str] = None,
                max_tokens: int = 1000,
                temperature: float = 0.7,
                stream: bool = False,
                **kwargs) -> Union[str, Iterator[str]]:
        """Generate text using Ollama."""
        if not self.is_initialized or not self.client:
            raise BackendNotAvailableError("Ollama backend not initialized")
        
        model = model or self.default_model
        
        # Map parameters to Ollama format
        options = {
            "num_predict": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        try:
            return self.client.generate(
                prompt=prompt,
                model=model,
                stream=stream,
                **options
            )
        except (OllamaConnectionError, OllamaModelError) as e:
            raise LLMBackendError(f"Ollama generation failed: {e}") from e
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             model: Optional[str] = None,
             max_tokens: int = 1000,
             temperature: float = 0.7,
             stream: bool = False,
             **kwargs) -> Union[str, Iterator[str]]:
        """Generate chat completion using Ollama."""
        if not self.is_initialized or not self.client:
            raise BackendNotAvailableError("Ollama backend not initialized")
        
        model = model or self.default_model
        
        # Map parameters to Ollama format
        options = {
            "num_predict": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        try:
            return self.client.chat(
                messages=messages,
                model=model,
                stream=stream,
                **options
            )
        except (OllamaConnectionError, OllamaModelError) as e:
            raise LLMBackendError(f"Ollama chat failed: {e}") from e
    
    def embed(self, 
              input_text: Union[str, List[str]], 
              model: Optional[str] = None) -> Union[List[float], List[List[float]]]:
        """Generate embeddings using Ollama."""
        if not self.is_initialized or not self.client:
            raise BackendNotAvailableError("Ollama backend not initialized")
        
        model = model or self.default_embed_model
        
        try:
            return self.client.embed(input_text=input_text, model=model)
        except (OllamaConnectionError, OllamaModelError) as e:
            raise LLMBackendError(f"Ollama embedding failed: {e}") from e
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        if not self.is_initialized or not self.client:
            raise BackendNotAvailableError("Ollama backend not initialized")
        
        try:
            models = self.client.list_models()
            return [model["name"] for model in models]
        except (OllamaConnectionError, OllamaModelError) as e:
            raise LLMBackendError(f"Failed to list Ollama models: {e}") from e
    
    def is_model_available(self, model: str) -> bool:
        """Check if a model is available in Ollama."""
        try:
            available_models = self.list_models()
            return model in available_models
        except LLMBackendError:
            return False
    
    def load_model(self, model: str) -> bool:
        """Load a model in Ollama (models are loaded on-demand)."""
        if not self.is_initialized or not self.client:
            raise BackendNotAvailableError("Ollama backend not initialized")
        
        try:
            # In Ollama, models are loaded on-demand, but we can verify it exists
            if self.is_model_available(model):
                self.current_model = model
                logger.info(f"Model {model} set as current model")
                return True
            else:
                logger.error(f"Model {model} not available")
                return False
        except Exception as e:
            logger.error(f"Failed to load model {model}: {e}")
            return False
    
    def unload_model(self) -> bool:
        """Unload current model (Ollama handles this automatically)."""
        self.current_model = None
        logger.info("Current model unloaded")
        return True
    
    def is_available(self) -> bool:
        """Check if Ollama backend is available."""
        if not self.client:
            return False
        return self.client.is_available()


class LlamaCppBackend(LLMBackend):
    """llama-cpp-python backend implementation."""
    
    def __init__(self, 
                 model_path: Optional[str] = None,
                 n_ctx: int = 4096,
                 n_batch: int = 512,
                 n_threads: Optional[int] = None,
                 **kwargs):
        """Initialize llama-cpp-python backend.
        
        Args:
            model_path: Path to GGUF model file
            n_ctx: Context window size
            n_batch: Batch size for processing
            n_threads: Number of threads (None for auto)
            **kwargs: Additional llama-cpp-python parameters
        """
        super().__init__(**kwargs)
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_batch = n_batch
        self.n_threads = n_threads
        self.model = None
        
        # Try to import llama-cpp-python
        try:
            from llama_cpp import Llama
            self.Llama = Llama
            self.llama_cpp_available = True
        except ImportError:
            self.Llama = None
            self.llama_cpp_available = False
            logger.warning("llama-cpp-python not available")
    
    def initialize(self) -> bool:
        """Initialize the llama-cpp-python model."""
        if not self.llama_cpp_available:
            logger.error("llama-cpp-python is not installed")
            return False
        
        if not self.model_path:
            logger.error("No model path specified for llama-cpp-python backend")
            return False
        
        if not Path(self.model_path).exists():
            logger.error(f"Model file not found: {self.model_path}")
            return False
        
        try:
            model_kwargs = {
                "model_path": self.model_path,
                "n_ctx": self.n_ctx,
                "n_batch": self.n_batch,
                "n_threads": self.n_threads,
                "verbose": False,
                **self.config
            }
            
            self.model = self.Llama(**model_kwargs)
            self.is_initialized = True
            self.current_model = Path(self.model_path).name
            logger.info(f"llama-cpp-python backend initialized with model: {self.current_model}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize llama-cpp-python backend: {e}")
            return False
    
    def generate(self, 
                prompt: str, 
                model: Optional[str] = None,
                max_tokens: int = 1000,
                temperature: float = 0.7,
                stream: bool = False,
                **kwargs) -> Union[str, Iterator[str]]:
        """Generate text using llama-cpp-python."""
        if not self.is_initialized or not self.model:
            raise BackendNotAvailableError("llama-cpp-python backend not initialized")
        
        generation_kwargs = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": kwargs.get("top_p", 0.9),
            "top_k": kwargs.get("top_k", 40),
            "repeat_penalty": kwargs.get("repeat_penalty", 1.1),
            "stop": kwargs.get("stop", ["</s>", "\n\n"]),
            "stream": stream
        }
        
        try:
            response = self.model(prompt, **generation_kwargs)
            
            if stream:
                return self._extract_streaming_text(response)
            else:
                # Extract text from response
                if isinstance(response, dict) and "choices" in response:
                    text = response["choices"][0]["text"].strip()
                else:
                    text = str(response).strip()
                
                return self._clean_response(text)
                
        except Exception as e:
            raise LLMBackendError(f"llama-cpp-python generation failed: {e}") from e
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             model: Optional[str] = None,
             max_tokens: int = 1000,
             temperature: float = 0.7,
             stream: bool = False,
             **kwargs) -> Union[str, Iterator[str]]:
        """Generate chat completion using llama-cpp-python."""
        if not self.is_initialized or not self.model:
            raise BackendNotAvailableError("llama-cpp-python backend not initialized")
        
        # Convert messages to prompt format
        prompt = self._messages_to_prompt(messages)
        
        return self.generate(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            **kwargs
        )
    
    def embed(self, 
              input_text: Union[str, List[str]], 
              model: Optional[str] = None) -> Union[List[float], List[List[float]]]:
        """Generate embeddings using llama-cpp-python."""
        if not self.is_initialized or not self.model:
            raise BackendNotAvailableError("llama-cpp-python backend not initialized")
        
        try:
            if isinstance(input_text, str):
                # Single text input
                embedding = self.model.embed(input_text)
                return embedding
            else:
                # Multiple text inputs
                embeddings = []
                for text in input_text:
                    embedding = self.model.embed(text)
                    embeddings.append(embedding)
                return embeddings
                
        except Exception as e:
            raise LLMBackendError(f"llama-cpp-python embedding failed: {e}") from e
    
    def list_models(self) -> List[str]:
        """List available models (returns current model if loaded)."""
        if self.current_model:
            return [self.current_model]
        return []
    
    def is_model_available(self, model: str) -> bool:
        """Check if a model file exists."""
        if model == self.current_model:
            return True
        
        # Check if it's a file path
        return Path(model).exists()
    
    def load_model(self, model: str) -> bool:
        """Load a new model file."""
        if not self.llama_cpp_available:
            return False
        
        if not Path(model).exists():
            logger.error(f"Model file not found: {model}")
            return False
        
        try:
            # Unload current model
            if self.model:
                del self.model
                self.model = None
            
            # Load new model
            self.model_path = model
            return self.initialize()
            
        except Exception as e:
            logger.error(f"Failed to load model {model}: {e}")
            return False
    
    def unload_model(self) -> bool:
        """Unload the current model."""
        try:
            if self.model:
                del self.model
                self.model = None
                self.current_model = None
                self.is_initialized = False
                logger.info("Model unloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to unload model: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if llama-cpp-python backend is available."""
        return self.llama_cpp_available and self.is_initialized
    
    def _extract_streaming_text(self, response_stream) -> Iterator[str]:
        """Extract text from streaming response."""
        for chunk in response_stream:
            if isinstance(chunk, dict) and "choices" in chunk:
                text = chunk["choices"][0].get("text", "")
                if text:
                    yield text
    
    def _clean_response(self, text: str) -> str:
        """Clean response text from chat format artifacts."""
        # Remove common chat format artifacts
        text = text.replace("[/INST]", "").replace("[INST]", "")
        text = text.replace("<s>", "").replace("</s>", "")
        return text.strip()
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a prompt format."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)


class LLMFactory:
    """Factory class for creating LLM backends."""
    
    @staticmethod
    def create_backend(backend_type: str, **kwargs) -> LLMBackend:
        """Create an LLM backend instance.
        
        Args:
            backend_type: Type of backend ('ollama' or 'llama-cpp')
            **kwargs: Configuration parameters for the backend
            
        Returns:
            LLMBackend instance
            
        Raises:
            ValueError: If backend_type is not supported
        """
        backend_type = backend_type.lower()
        
        if backend_type == "ollama":
            return OllamaBackend(**kwargs)
        elif backend_type in ["llama-cpp", "llama_cpp", "llamacpp"]:
            return LlamaCppBackend(**kwargs)
        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")
    
    @staticmethod
    def get_available_backends() -> List[str]:
        """Get list of available backend types.
        
        Returns:
            List of available backend type names
        """
        backends = ["ollama"]
        
        # Check if llama-cpp-python is available
        try:
            import llama_cpp
            backends.append("llama-cpp")
        except ImportError:
            pass
        
        return backends


class LLMContext:
    """Context class that uses the Strategy pattern for LLM operations."""
    
    def __init__(self, backend: LLMBackend):
        """Initialize with a specific backend.
        
        Args:
            backend: LLMBackend instance to use
        """
        self.backend = backend
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize the current backend.
        
        Returns:
            True if initialization successful, False otherwise
        """
        self._initialized = self.backend.initialize()
        return self._initialized
    
    def switch_backend(self, new_backend: LLMBackend) -> bool:
        """Switch to a different backend.
        
        Args:
            new_backend: New LLMBackend instance to use
            
        Returns:
            True if switch successful, False otherwise
        """
        try:
            if new_backend.initialize():
                self.backend = new_backend
                self._initialized = True
                logger.info(f"Switched to backend: {new_backend.__class__.__name__}")
                return True
            else:
                logger.error(f"Failed to initialize new backend: {new_backend.__class__.__name__}")
                return False
        except Exception as e:
            logger.error(f"Error switching backend: {e}")
            return False
    
    def generate(self, *args, **kwargs) -> Union[str, Iterator[str]]:
        """Generate text using the current backend."""
        if not self._initialized:
            raise BackendNotAvailableError("Backend not initialized")
        return self.backend.generate(*args, **kwargs)
    
    def chat(self, *args, **kwargs) -> Union[str, Iterator[str]]:
        """Generate chat completion using the current backend."""
        if not self._initialized:
            raise BackendNotAvailableError("Backend not initialized")
        return self.backend.chat(*args, **kwargs)
    
    def embed(self, *args, **kwargs) -> Union[List[float], List[List[float]]]:
        """Generate embeddings using the current backend."""
        if not self._initialized:
            raise BackendNotAvailableError("Backend not initialized")
        return self.backend.embed(*args, **kwargs)
    
    def list_models(self) -> List[str]:
        """List available models."""
        if not self._initialized:
            raise BackendNotAvailableError("Backend not initialized")
        return self.backend.list_models()
    
    def is_model_available(self, model: str) -> bool:
        """Check if a model is available."""
        if not self._initialized:
            return False
        return self.backend.is_model_available(model)
    
    def load_model(self, model: str) -> bool:
        """Load a specific model."""
        if not self._initialized:
            raise BackendNotAvailableError("Backend not initialized")
        return self.backend.load_model(model)
    
    def unload_model(self) -> bool:
        """Unload the current model."""
        if not self._initialized:
            raise BackendNotAvailableError("Backend not initialized")
        return self.backend.unload_model()
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the current backend."""
        return self.backend.get_backend_info()
    
    def is_available(self) -> bool:
        """Check if the current backend is available."""
        return self._initialized and self.backend.is_available() 