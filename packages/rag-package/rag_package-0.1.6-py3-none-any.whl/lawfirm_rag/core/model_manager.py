"""
Model Manager for LawFirm-RAG

Handles loading, unloading, and managing multiple AI models.
Integrates with ModelDownloader and AIEngine classes.
"""

import os
import logging
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading

from .ai_engine import AIEngine
from .model_downloader import ModelDownloader
from .ai_engine import create_ai_engine_from_config
from ..utils.config import ConfigManager

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages multiple AI models, handling loading, unloading, and switching.
    
    Provides a centralized interface for model operations and memory management.
    """
    
    def __init__(self, models_dir: Optional[str] = None, max_loaded_models: int = 2):
        """
        Initialize the ModelManager.
        
        Args:
            models_dir: Directory containing downloaded models
            max_loaded_models: Maximum number of models to keep loaded simultaneously
        """
        if models_dir is None:
            models_dir = Path(__file__).parent.parent / "models" / "downloaded"
        
        self.models_dir = Path(models_dir)
        self.max_loaded_models = max_loaded_models
        
        # Track loaded models
        self.loaded_models: Dict[str, Dict[str, Any]] = {}
        self.active_model: Optional[str] = None
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize model downloader for discovery
        self.downloader = ModelDownloader(str(self.models_dir))
        
    def discover_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all available models through Ollama.
        
        Returns:
            Dictionary mapping model variants to their information
        """
        available_models = {}
        
        # Use the downloader's discovery functionality which works with Ollama
        downloader_models = self.downloader.list_available_models()
        
        for variant, info in downloader_models.items():
            if info["downloaded"] and info["available"]:
                # For Ollama models, use the model name as both path and identifier
                available_models[variant] = {
                    "variant": variant,
                    "path": variant,  # Use model name as path for Ollama
                    "size": info["size"],
                    "filename": variant,  # Use model name as filename
                    "description": info["description"],
                    "use_case": info["use_case"],
                    "type": info["type"],
                    "is_loaded": variant in self.loaded_models,
                    "is_active": variant == self.active_model
                }
        
        return available_models
    
    def load_model(self, model_variant: str, force_reload: bool = False) -> bool:
        """
        Load a model into memory using Ollama.
        
        Args:
            model_variant: The model variant to load
            force_reload: If True, reload even if already loaded
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        with self._lock:
            # Check if already loaded
            if model_variant in self.loaded_models and not force_reload:
                logger.info(f"Model {model_variant} is already loaded")
                self.active_model = model_variant
                return True
            
            # Discover available models
            available_models = self.discover_models()
            
            if model_variant not in available_models:
                logger.error(f"Model {model_variant} not found or not available in Ollama")
                return False
            
            # Check memory and unload models if necessary
            if len(self.loaded_models) >= self.max_loaded_models:
                self._unload_oldest_model()
            
            try:
                logger.info(f"Loading Ollama model {model_variant}")
                
                # Create AI engine instance using new configuration system
                config_manager = ConfigManager()
                config = config_manager.get_config()
                
                # Create AI engine with Ollama backend
                ai_engine = create_ai_engine_from_config(config)
                
                # For Ollama models, we don't need to load from a file path
                # The model should already be available in Ollama
                if not ai_engine.load_model():
                    logger.error(f"Failed to load Ollama model {model_variant}")
                    return False
                
                # Store loaded model info
                self.loaded_models[model_variant] = {
                    "ai_engine": ai_engine,
                    "model_path": model_variant,  # Store model name for Ollama
                    "loaded_at": datetime.now().isoformat(),
                    "memory_usage": self._estimate_memory_usage(),
                    "variant": model_variant,
                    "model_variant": model_variant,  # Add this for API compatibility
                    "is_active": True
                }
                
                # Set as active model
                self.active_model = model_variant
                
                logger.info(f"Successfully loaded Ollama model {model_variant}")
                return True
                
            except Exception as e:
                logger.error(f"Error loading Ollama model {model_variant}: {e}")
                return False
    
    def unload_model(self, model_variant: str) -> bool:
        """
        Unload a model from memory.
        
        Args:
            model_variant: The model variant to unload
            
        Returns:
            True if model unloaded successfully, False otherwise
        """
        with self._lock:
            if model_variant not in self.loaded_models:
                logger.warning(f"Model {model_variant} is not loaded")
                return False
            
            try:
                # Get the AI engine
                model_info = self.loaded_models[model_variant]
                ai_engine = model_info["ai_engine"]
                
                # Unload the model
                ai_engine.unload_model()
                
                # Remove from loaded models
                del self.loaded_models[model_variant]
                
                # Update active model
                if self.active_model == model_variant:
                    self.active_model = list(self.loaded_models.keys())[0] if self.loaded_models else None
                
                logger.info(f"Successfully unloaded model {model_variant}")
                return True
                
            except Exception as e:
                logger.error(f"Error unloading model {model_variant}: {e}")
                return False
    
    def switch_active_model(self, model_variant: str) -> bool:
        """
        Switch the active model without unloading others.
        
        Args:
            model_variant: The model variant to make active
            
        Returns:
            True if switch successful, False otherwise
        """
        with self._lock:
            if model_variant not in self.loaded_models:
                logger.error(f"Model {model_variant} is not loaded")
                return False
            
            self.active_model = model_variant
            logger.info(f"Switched active model to {model_variant}")
            return True
    
    def get_active_model(self) -> Optional[AIEngine]:
        """
        Get the currently active AI engine.
        
        Returns:
            The active AIEngine instance, or None if no model is active
        """
        if self.active_model and self.active_model in self.loaded_models:
            return self.loaded_models[self.active_model]["ai_engine"]
        return None
    
    def get_loaded_models(self) -> List[Dict[str, Any]]:
        """
        Get information about all loaded models.
        
        Returns:
            List of dictionaries containing model information
        """
        loaded_models = []
        
        for variant, info in self.loaded_models.items():
            loaded_models.append({
                "model_variant": variant,
                "model_path": info["model_path"],
                "loaded_at": info["loaded_at"],
                "memory_usage": info.get("memory_usage"),
                "is_active": variant == self.active_model
            })
        
        return loaded_models
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get overall status of the model manager.
        
        Returns:
            Dictionary containing status information
        """
        return {
            "loaded_models_count": len(self.loaded_models),
            "max_loaded_models": self.max_loaded_models,
            "active_model": self.active_model,
            "total_memory_usage": sum(
                info.get("memory_usage", 0) for info in self.loaded_models.values()
            ),
            "available_models": list(self.discover_models().keys())
        }
    
    def cleanup_all_models(self) -> None:
        """Unload all models and clean up resources."""
        with self._lock:
            for variant in list(self.loaded_models.keys()):
                self.unload_model(variant)
            
            self.active_model = None
            logger.info("All models unloaded and cleaned up")
    
    def _unload_oldest_model(self) -> None:
        """Unload the oldest loaded model to free memory."""
        if not self.loaded_models:
            return
        
        # Find the oldest model (by loaded_at timestamp)
        oldest_variant = min(
            self.loaded_models.keys(),
            key=lambda v: self.loaded_models[v]["loaded_at"]
        )
        
        logger.info(f"Unloading oldest model {oldest_variant} to free memory")
        self.unload_model(oldest_variant)
    
    def _estimate_memory_usage(self) -> int:
        """
        Estimate current memory usage in bytes.
        
        Returns:
            Estimated memory usage in bytes
        """
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except Exception as e:
            logger.warning(f"Could not estimate memory usage: {e}")
            return 0
    
    def __del__(self):
        """Cleanup when the manager is destroyed."""
        try:
            self.cleanup_all_models()
        except Exception as e:
            logger.error(f"Error during ModelManager cleanup: {e}") 