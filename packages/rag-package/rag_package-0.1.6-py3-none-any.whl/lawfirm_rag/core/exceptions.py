"""
Custom exceptions for LawFirm-RAG.

Provides user-friendly error messages and troubleshooting guidance for common issues.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LawFirmRAGError(Exception):
    """Base exception for LawFirm-RAG errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}
        self.user_message = message
        self.troubleshooting_steps = []
    
    def add_troubleshooting_step(self, step: str) -> None:
        """Add a troubleshooting step to the error."""
        self.troubleshooting_steps.append(step)
    
    def get_user_friendly_message(self) -> str:
        """Get a user-friendly error message with troubleshooting steps."""
        message = f"❌ {self.user_message}\n"
        
        if self.troubleshooting_steps:
            message += "\n🔧 Troubleshooting Steps:\n"
            for i, step in enumerate(self.troubleshooting_steps, 1):
                message += f"   {i}. {step}\n"
        
        if self.details:
            message += f"\n📋 Technical Details: {self.details}\n"
        
        return message


class ModelError(LawFirmRAGError):
    """Base exception for model-related errors."""
    
    def __init__(self, message: str, model_name: Optional[str] = None, model_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.model_type = model_type


class ModelNotFoundError(ModelError):
    """Raised when a specified model is not found in Ollama."""
    
    def __init__(self, model_name: str, model_type: Optional[str] = None, available_models: Optional[list] = None):
        model_type_desc = f" ({model_type})" if model_type else ""
        message = f"Model '{model_name}'{model_type_desc} not found in Ollama"
        
        super().__init__(message, model_name=model_name, model_type=model_type)
        
        # Add troubleshooting steps
        self.add_troubleshooting_step(f"Pull the model: ollama pull {model_name}")
        self.add_troubleshooting_step("Check if Ollama is running: ollama list")
        self.add_troubleshooting_step("Verify Ollama server is accessible at the configured URL")
        
        if model_type:
            self.add_troubleshooting_step(f"Update your config.yaml to use a different {model_type} model")
        
        if available_models:
            self.add_troubleshooting_step(f"Available models: {', '.join(available_models[:5])}")
            self.details["available_models"] = available_models


class ModelLoadError(ModelError):
    """Raised when a model exists but fails to load."""
    
    def __init__(self, model_name: str, model_type: Optional[str] = None, original_error: Optional[Exception] = None):
        model_type_desc = f" ({model_type})" if model_type else ""
        message = f"Failed to load model '{model_name}'{model_type_desc}"
        
        super().__init__(message, model_name=model_name, model_type=model_type)
        
        if original_error:
            self.details["original_error"] = str(original_error)
        
        # Add troubleshooting steps
        self.add_troubleshooting_step("Check Ollama server logs for detailed error information")
        self.add_troubleshooting_step(f"Try restarting Ollama and pulling the model again: ollama pull {model_name}")
        self.add_troubleshooting_step("Verify you have sufficient memory and disk space")
        self.add_troubleshooting_step("Check if the model file is corrupted and re-download if necessary")


class ModelTimeoutError(ModelError):
    """Raised when model operations exceed time limits."""
    
    def __init__(self, model_name: str, operation: str, timeout: int, model_type: Optional[str] = None):
        model_type_desc = f" ({model_type})" if model_type else ""
        message = f"Timeout after {timeout}s waiting for {operation} with model '{model_name}'{model_type_desc}"
        
        super().__init__(message, model_name=model_name, model_type=model_type)
        self.details.update({"operation": operation, "timeout": timeout})
        
        # Add troubleshooting steps
        self.add_troubleshooting_step("Increase timeout in configuration if the model is slow to respond")
        self.add_troubleshooting_step("Check Ollama server performance and resource usage")
        self.add_troubleshooting_step("Try using a smaller/faster model variant")
        self.add_troubleshooting_step("Verify network connectivity to Ollama server")


class ConfigurationError(LawFirmRAGError):
    """Raised when there are configuration-related issues."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        
        # Add general troubleshooting steps
        self.add_troubleshooting_step("Check your config.yaml file for syntax errors")
        self.add_troubleshooting_step("Verify all required configuration sections are present")
        
        if config_key:
            self.add_troubleshooting_step(f"Review the '{config_key}' configuration section")


class BackendNotAvailableError(LawFirmRAGError):
    """Raised when no suitable LLM backend is available."""
    
    def __init__(self, attempted_backends: Optional[list] = None):
        message = "No suitable LLM backend is available"
        super().__init__(message)
        
        if attempted_backends:
            self.details["attempted_backends"] = attempted_backends
        
        # Add troubleshooting steps
        self.add_troubleshooting_step("Install and start Ollama: https://ollama.ai")
        self.add_troubleshooting_step("Pull at least one model: ollama pull llama3.2")
        self.add_troubleshooting_step("Verify Ollama is running: ollama list")
        self.add_troubleshooting_step("Check your configuration file for correct backend settings")


def log_and_raise_model_error(error: ModelError, logger_instance: Optional[logging.Logger] = None) -> None:
    """Log a model error and raise it with user-friendly formatting.
    
    Args:
        error: The model error to log and raise
        logger_instance: Logger to use (defaults to module logger)
    """
    log = logger_instance or logger
    
    # Log the error with appropriate level
    if isinstance(error, ModelTimeoutError):
        log.warning(f"Model timeout: {error}")
    elif isinstance(error, ModelNotFoundError):
        log.error(f"Model not found: {error}")
    elif isinstance(error, ModelLoadError):
        log.error(f"Model load failed: {error}")
    else:
        log.error(f"Model error: {error}")
    
    # Log troubleshooting steps at debug level
    if error.troubleshooting_steps:
        log.debug(f"Troubleshooting steps for {error.__class__.__name__}: {error.troubleshooting_steps}")
    
    raise error


def create_model_not_found_error(model_name: str, model_type: str, available_models: Optional[list] = None) -> ModelNotFoundError:
    """Create a ModelNotFoundError with appropriate context.
    
    Args:
        model_name: Name of the missing model
        model_type: Type of model (chat, legal_analysis, etc.)
        available_models: List of available models
        
    Returns:
        Configured ModelNotFoundError
    """
    error = ModelNotFoundError(model_name, model_type, available_models)
    
    # Add model-type specific troubleshooting
    if model_type == "legal_analysis":
        error.add_troubleshooting_step("For legal analysis, try: ollama pull hf.co/TheBloke/law-chat-GGUF:Q4_0")
    elif model_type == "embeddings":
        error.add_troubleshooting_step("For embeddings, try: ollama pull mxbai-embed-large")
    elif model_type == "chat":
        error.add_troubleshooting_step("For chat, try: ollama pull llama3.2")
    
    return error 