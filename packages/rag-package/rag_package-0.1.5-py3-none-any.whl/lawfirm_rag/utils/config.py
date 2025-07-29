"""
Configuration management module for LawFirm-RAG.

Handles loading, saving, and managing configuration settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration settings for LawFirm-RAG."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default locations.
        """
        self.config_path = self._resolve_config_path(config_path)
        self.config_data = self._load_config()
        
        # Automatically migrate legacy configuration if needed
        self.migrate_legacy_config()
        
    def _resolve_config_path(self, config_path: Optional[str]) -> Path:
        """Resolve the configuration file path.
        
        Args:
            config_path: User-provided config path.
            
        Returns:
            Resolved configuration file path.
        """
        if config_path:
            return Path(config_path).expanduser().resolve()
        
        # Check environment variable
        env_config = os.getenv("LAWFIRM_RAG_CONFIG_PATH")
        if env_config:
            return Path(env_config).expanduser().resolve()
        
        # Default locations
        config_dir = Path.home() / ".lawfirm-rag"
        return config_dir / "config.yaml"
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary.
        """
        if not self.config_path.exists():
            logger.info(f"Configuration file not found at {self.config_path}, using defaults")
            return self._get_default_config()
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            
            # Merge with defaults to ensure all keys exist
            default_config = self._get_default_config()
            merged_config = self._merge_configs(default_config, config)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return merged_config
            
        except Exception as e:
            logger.error(f"Error loading configuration from {self.config_path}: {e}")
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary.
        """
        return {
            "llm": {
                "backend": "ollama",  # Force Ollama instead of auto-detection
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "default_model": "law-chat",
                    "default_embed_model": "mxbai-embed-large",
                    "timeout": 30,
                    "max_retries": 3,
                    "retry_delay": 1.0
                },
                "llama_cpp": {
                    "model_path": "~/.lawfirm-rag/models/default.gguf",
                    "n_ctx": 4096,
                    "n_batch": 512,
                    "n_threads": None,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            # Legacy model section for backward compatibility
            "model": {
                "path": "~/.lawfirm-rag/models/default.gguf",
                "context_length": 4096,
                "threads": None,
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "api": {
                "host": "127.0.0.1",
                "port": 8000,
                "cors_origins": ["*"],
                "api_key": None
            },
            "processing": {
                "temp_dir": "~/.lawfirm-rag/temp",
                "max_file_size": "100MB",
                "supported_formats": ["pdf", "docx", "txt"]
            },
            "databases": {
                "westlaw": {
                    "default_operators": ["&", "|"],
                    "proximity_operators": ["/s", "/p"]
                },
                "lexisnexis": {
                    "default_operators": ["AND", "OR", "NOT"],
                    "proximity_operators": ["W/n", "PRE/n"]
                },
                "casetext": {
                    "default_operators": ["AND", "OR", "NOT"],
                    "proximity_operators": ["NEAR"]
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with defaults.
        
        Args:
            default: Default configuration
            user: User configuration
            
        Returns:
            Merged configuration
        """
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
                
        return merged
        
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration.
        
        Returns:
            Configuration dictionary.
        """
        return self.config_data.copy()
        
    def get_option(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration option.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'model.path')
            default: Default value if key not found
            
        Returns:
            Configuration value or default.
        """
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set_option(self, key: str, value: Any) -> None:
        """Set a configuration option.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config_data
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Set the value
        config[keys[-1]] = value
        
        # Save the configuration
        self.save_config()
        
    def save_config(self) -> None:
        """Save the current configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
                
            logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration to {self.config_path}: {e}")
            raise
            
    def create_default_config(self) -> None:
        """Create a default configuration file."""
        self.config_data = self._get_default_config()
        self.save_config()
        
    def get_models_dir(self) -> Path:
        """Get the models directory path.
        
        Returns:
            Path to models directory.
        """
        model_path = self.get_option("model.path", "~/.lawfirm-rag/models/default.gguf")
        return Path(model_path).expanduser().parent
        
    def get_temp_dir(self) -> Path:
        """Get the temporary directory path.
        
        Returns:
            Path to temporary directory.
        """
        temp_dir = self.get_option("processing.temp_dir", "~/.lawfirm-rag/temp")
        return Path(temp_dir).expanduser()
        
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.config_path.parent,
            self.get_models_dir(),
            self.get_temp_dir()
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def get_llm_backend(self) -> str:
        """Get the configured LLM backend type.
        
        Returns:
            Backend type string ("auto", "ollama", "llama-cpp")
        """
        return self.get_option("llm.backend", "auto")
    
    def set_llm_backend(self, backend: str) -> None:
        """Set the LLM backend type.
        
        Args:
            backend: Backend type ("auto", "ollama", "llama-cpp")
        """
        if backend not in ["auto", "ollama", "llama-cpp"]:
            raise ValueError(f"Invalid backend type: {backend}")
        self.set_option("llm.backend", backend)
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama backend configuration.
        
        Returns:
            Ollama configuration dictionary
        """
        return self.get_option("llm.ollama", {})
    
    def get_llama_cpp_config(self) -> Dict[str, Any]:
        """Get llama-cpp-python backend configuration.
        
        Returns:
            llama-cpp-python configuration dictionary
        """
        return self.get_option("llm.llama_cpp", {})
    
    def get_llm_config_for_backend(self, backend: str) -> Dict[str, Any]:
        """Get configuration for a specific backend.
        
        Args:
            backend: Backend type ("ollama" or "llama-cpp")
            
        Returns:
            Backend-specific configuration dictionary
        """
        if backend == "ollama":
            return self.get_ollama_config()
        elif backend in ["llama-cpp", "llama_cpp", "llamacpp"]:
            return self.get_llama_cpp_config()
        else:
            raise ValueError(f"Unknown backend type: {backend}")
    
    def migrate_legacy_config(self) -> bool:
        """Migrate legacy model configuration to new LLM structure.
        
        Returns:
            True if migration was performed, False if not needed
        """
        # Check if we have legacy config but no new LLM config
        legacy_model = self.get_option("model", {})
        llm_config = self.get_option("llm", {})
        
        # If we have a legacy model path but no LLM backend config, migrate
        if legacy_model.get("path") and not llm_config.get("backend"):
            logger.info("Migrating legacy model configuration to new LLM structure")
            
            # Set backend to llama-cpp since legacy used direct model paths
            self.set_option("llm.backend", "llama-cpp")
            
            # Migrate model settings
            if "path" in legacy_model:
                self.set_option("llm.llama_cpp.model_path", legacy_model["path"])
            if "context_length" in legacy_model:
                self.set_option("llm.llama_cpp.n_ctx", legacy_model["context_length"])
            if "threads" in legacy_model:
                self.set_option("llm.llama_cpp.n_threads", legacy_model["threads"])
            if "temperature" in legacy_model:
                self.set_option("llm.llama_cpp.temperature", legacy_model["temperature"])
            if "max_tokens" in legacy_model:
                self.set_option("llm.llama_cpp.max_tokens", legacy_model["max_tokens"])
            
            logger.info("Legacy configuration migration completed")
            return True
        
        return False 