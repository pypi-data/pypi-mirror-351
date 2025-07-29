"""
Ollama Client Interface for LawFirm-RAG.

Provides a client interface to communicate with the Ollama API,
supporting all current LLM operations including text generation,
embeddings, and model management.
"""

import logging
import time
from typing import Optional, Dict, Any, List, Union, Iterator
import json
import requests
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class OllamaConnectionError(Exception):
    """Raised when connection to Ollama server fails."""
    pass


class OllamaModelError(Exception):
    """Raised when model operations fail."""
    pass


class OllamaClient:
    """Client interface for communicating with Ollama API."""
    
    def __init__(self, 
                 base_url: str = None,
                 timeout: int = 30,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        """Initialize the Ollama client.
        
        Args:
            base_url: Base URL for Ollama API. Defaults to http://localhost:11434
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        
        # Remove trailing slash if present
        self.base_url = self.base_url.rstrip('/')
        
        logger.info(f"Initialized Ollama client with base URL: {self.base_url}")
    
    def _make_request(self, 
                     method: str, 
                     endpoint: str, 
                     data: Optional[Dict[str, Any]] = None,
                     stream: bool = False) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Make a request to the Ollama API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request data for POST requests
            stream: Whether to stream the response
            
        Returns:
            Response data or iterator for streaming responses
            
        Raises:
            OllamaConnectionError: If connection fails after retries
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=self.timeout, stream=stream)
                elif method.upper() == 'POST':
                    response = self.session.post(
                        url, 
                        json=data, 
                        timeout=self.timeout, 
                        stream=stream
                    )
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                
                if stream:
                    return self._parse_streaming_response(response)
                else:
                    return response.json() if response.content else {}
                    
            except requests.exceptions.ConnectionError as e:
                if attempt == self.max_retries:
                    raise OllamaConnectionError(
                        f"Failed to connect to Ollama server at {self.base_url} after {self.max_retries + 1} attempts. "
                        f"Make sure Ollama is running and accessible."
                    ) from e
                
                logger.warning(f"Connection attempt {attempt + 1} failed, retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    raise OllamaModelError(f"Model not found: {e.response.text}")
                elif e.response.status_code == 400:
                    raise OllamaModelError(f"Bad request: {e.response.text}")
                else:
                    raise OllamaConnectionError(f"HTTP error {e.response.status_code}: {e.response.text}")
                    
            except Exception as e:
                if attempt == self.max_retries:
                    raise OllamaConnectionError(f"Unexpected error: {e}") from e
                
                logger.warning(f"Request attempt {attempt + 1} failed: {e}, retrying...")
                time.sleep(self.retry_delay)
    
    def _parse_streaming_response(self, response: requests.Response) -> Iterator[Dict[str, Any]]:
        """Parse streaming JSON response from Ollama API.
        
        Args:
            response: Streaming HTTP response
            
        Yields:
            Parsed JSON objects from the stream
        """
        for line in response.iter_lines():
            if line:
                try:
                    yield json.loads(line.decode('utf-8'))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse streaming response line: {line}, error: {e}")
                    continue
    
    def generate(self, 
                prompt: str, 
                model: str = "llama3.2",
                stream: bool = False,
                **options) -> Union[str, Iterator[str]]:
        """Generate text completion using Ollama.
        
        Args:
            prompt: Input prompt for text generation
            model: Model name to use for generation
            stream: Whether to stream the response
            **options: Additional generation options (temperature, max_tokens, etc.)
            
        Returns:
            Generated text or iterator for streaming responses
        """
        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            **options
        }
        
        if stream:
            response_stream = self._make_request("POST", "/api/generate", data, stream=True)
            return self._extract_streaming_text(response_stream)
        else:
            response = self._make_request("POST", "/api/generate", data)
            return response.get("response", "")
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             model: str = "llama3.2",
             stream: bool = False,
             **options) -> Union[str, Iterator[str]]:
        """Generate chat completion using Ollama.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use for chat
            stream: Whether to stream the response
            **options: Additional chat options
            
        Returns:
            Generated response or iterator for streaming responses
        """
        data = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **options
        }
        
        if stream:
            response_stream = self._make_request("POST", "/api/chat", data, stream=True)
            return self._extract_streaming_chat_text(response_stream)
        else:
            response = self._make_request("POST", "/api/chat", data)
            return response.get("message", {}).get("content", "")
    
    def embed(self, 
              input_text: Union[str, List[str]], 
              model: str = "mxbai-embed-large") -> Union[List[float], List[List[float]]]:
        """Generate embeddings using Ollama.
        
        Args:
            input_text: Text or list of texts to embed
            model: Embedding model name
            
        Returns:
            Embedding vector(s)
        """
        data = {
            "model": model,
            "input": input_text
        }
        
        response = self._make_request("POST", "/api/embed", data)
        embeddings = response.get("embeddings", [])
        
        # Return single embedding for single input, list for multiple inputs
        if isinstance(input_text, str):
            return embeddings[0] if embeddings else []
        else:
            return embeddings
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models in Ollama.
        
        Returns:
            List of model information dictionaries
        """
        response = self._make_request("GET", "/api/tags")
        return response.get("models", [])
    
    def show_model(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a specific model.
        
        Args:
            model: Model name
            
        Returns:
            Model information dictionary
        """
        data = {"model": model}
        return self._make_request("POST", "/api/show", data)
    
    def pull_model(self, model: str, stream: bool = True) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Pull/download a model from Ollama library.
        
        Args:
            model: Model name to pull
            stream: Whether to stream download progress
            
        Returns:
            Pull status or iterator for streaming progress
        """
        data = {"model": model, "stream": stream}
        return self._make_request("POST", "/api/pull", data, stream=stream)
    
    def delete_model(self, model: str) -> Dict[str, Any]:
        """Delete a model from Ollama.
        
        Args:
            model: Model name to delete
            
        Returns:
            Deletion status
        """
        data = {"model": model}
        return self._make_request("DELETE", "/api/delete", data)
    
    def copy_model(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy a model to a new name.
        
        Args:
            source: Source model name
            destination: Destination model name
            
        Returns:
            Copy status
        """
        data = {"source": source, "destination": destination}
        return self._make_request("POST", "/api/copy", data)
    
    def list_running_models(self) -> List[Dict[str, Any]]:
        """List currently running models.
        
        Returns:
            List of running model information
        """
        response = self._make_request("GET", "/api/ps")
        return response.get("models", [])
    
    def _extract_streaming_text(self, response_stream: Iterator[Dict[str, Any]]) -> Iterator[str]:
        """Extract text from streaming generate response.
        
        Args:
            response_stream: Iterator of response dictionaries
            
        Yields:
            Text chunks from the stream
        """
        for chunk in response_stream:
            if "response" in chunk:
                yield chunk["response"]
    
    def _extract_streaming_chat_text(self, response_stream: Iterator[Dict[str, Any]]) -> Iterator[str]:
        """Extract text from streaming chat response.
        
        Args:
            response_stream: Iterator of response dictionaries
            
        Yields:
            Text chunks from the stream
        """
        for chunk in response_stream:
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]
    
    def is_available(self) -> bool:
        """Check if Ollama server is available.
        
        Returns:
            True if server is reachable, False otherwise
        """
        try:
            self._make_request("GET", "/api/tags")
            return True
        except (OllamaConnectionError, OllamaModelError):
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the Ollama server.
        
        Returns:
            Health status information
        """
        try:
            models = self.list_models()
            running_models = self.list_running_models()
            
            return {
                "status": "healthy",
                "base_url": self.base_url,
                "total_models": len(models),
                "running_models": len(running_models),
                "available_models": [m["name"] for m in models],
                "running_model_names": [m["name"] for m in running_models]
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "base_url": self.base_url,
                "error": str(e)
            }
    
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 