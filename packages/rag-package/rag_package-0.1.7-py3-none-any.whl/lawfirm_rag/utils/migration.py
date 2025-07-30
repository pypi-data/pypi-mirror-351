"""
Migration utilities for LawFirm-RAG.

Provides tools for migrating configurations and detecting backend compatibility.
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .config import DEFAULT_MODELS, get_model_name

logger = logging.getLogger(__name__)


class ConfigMigrator:
    """Handles migration of configuration files to new LLM backend structure."""
    
    def __init__(self):
        """Initialize the configuration migrator."""
        self.migration_log = []
        self.supported_versions = ["legacy", "1.0"]
    
    def detect_config_version(self, config: Dict[str, Any]) -> str:
        """Detect the version/format of a configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Version string ("legacy", "v1", "unknown")
        """
        if "llm" in config and "backend" in config["llm"]:
            return "v1"  # New format
        elif "model" in config and "path" in config["model"]:
            return "legacy"  # Old format
        else:
            return "unknown"
    
    def migrate_config(self, config: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Migrate a configuration to the new format.
        
        Args:
            config: Original configuration dictionary
            
        Returns:
            Tuple of (migrated_config, migration_notes)
        """
        version = self.detect_config_version(config)
        migration_notes = []
        
        if version == "v1":
            migration_notes.append("Configuration is already in the new format")
            return config.copy(), migration_notes
        
        if version == "legacy":
            return self._migrate_legacy_config(config, migration_notes)
        
        # Unknown format - create minimal new config
        migration_notes.append("Unknown configuration format, creating new default configuration")
        return self._create_default_v1_config(), migration_notes
    
    def _migrate_legacy_config(self, config: Dict[str, Any], notes: List[str]) -> Tuple[Dict[str, Any], List[str]]:
        """Migrate legacy configuration to v1.0 format.
        
        Args:
            config: Legacy configuration dictionary
            notes: List to append migration notes to
            
        Returns:
            Tuple of (migrated_config, updated_notes)
        """
        notes.append("Migrating legacy configuration to v1.0 format")
        
        # Start with default v1 configuration
        migrated = self._create_default_v1_config()
        
        # Preserve any existing non-model settings
        for key, value in config.items():
            if key not in ["model", "llm"]:  # Don't copy legacy model or partial llm configs
                migrated[key] = value
                notes.append(f"Preserved existing setting: {key}")
        
        # Handle legacy model configuration
        legacy_model = config.get("model", {})
        
        # Create new LLM structure
        llm_config = {
            "backend": "llama-cpp",  # Legacy always used direct model paths
            "ollama": {
                "base_url": "http://localhost:11434",
                "default_model": get_model_name("chat"),
                "default_embed_model": get_model_name("embeddings"),
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
        }
        
        # Migrate legacy model settings
        if "path" in legacy_model:
            llm_config["llama_cpp"]["model_path"] = legacy_model["path"]
            notes.append(f"Migrated model path: {legacy_model['path']}")
        
        if "context_length" in legacy_model:
            llm_config["llama_cpp"]["n_ctx"] = legacy_model["context_length"]
            notes.append(f"Migrated context length: {legacy_model['context_length']}")
        
        if "threads" in legacy_model:
            llm_config["llama_cpp"]["n_threads"] = legacy_model["threads"]
            notes.append(f"Migrated thread count: {legacy_model['threads']}")
        
        if "temperature" in legacy_model:
            llm_config["llama_cpp"]["temperature"] = legacy_model["temperature"]
            notes.append(f"Migrated temperature: {legacy_model['temperature']}")
        
        if "max_tokens" in legacy_model:
            llm_config["llama_cpp"]["max_tokens"] = legacy_model["max_tokens"]
            notes.append(f"Migrated max tokens: {legacy_model['max_tokens']}")
        
        # Add the new LLM configuration
        migrated["llm"] = llm_config
        
        notes.append("Successfully migrated legacy configuration to new LLM backend structure")
        notes.append("Legacy 'model' section preserved for backward compatibility")
        
        return migrated, notes
    
    def _create_default_v1_config(self) -> Dict[str, Any]:
        """Create a default v1 configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "llm": {
                "backend": "auto",
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "default_model": get_model_name("chat"),
                    "default_embed_model": get_model_name("embeddings"),
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
            # Model configuration for different use cases
            "models": DEFAULT_MODELS.copy(),
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
    
    def migrate_config_file(self, 
                           input_path: str, 
                           output_path: Optional[str] = None,
                           backup: bool = True) -> Dict[str, Any]:
        """Migrate a configuration file.
        
        Args:
            input_path: Path to input configuration file
            output_path: Path for output file (defaults to input_path)
            backup: Whether to create a backup of the original file
            
        Returns:
            Migration result dictionary
        """
        input_path = Path(input_path).expanduser().resolve()
        output_path = Path(output_path).expanduser().resolve() if output_path else input_path
        
        result = {
            "success": False,
            "input_path": str(input_path),
            "output_path": str(output_path),
            "backup_path": None,
            "migration_notes": [],
            "errors": []
        }
        
        try:
            # Check if input file exists
            if not input_path.exists():
                result["errors"].append(f"Input file not found: {input_path}")
                return result
            
            # Load original configuration
            with open(input_path, "r", encoding="utf-8") as f:
                if input_path.suffix.lower() in [".yaml", ".yml"]:
                    original_config = yaml.safe_load(f) or {}
                elif input_path.suffix.lower() == ".json":
                    original_config = json.load(f)
                else:
                    result["errors"].append(f"Unsupported file format: {input_path.suffix}")
                    return result
            
            # Migrate configuration
            migrated_config, migration_notes = self.migrate_config(original_config)
            result["migration_notes"] = migration_notes
            
            # Create backup if requested
            if backup and input_path == output_path:
                backup_path = input_path.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}{input_path.suffix}")
                backup_path.write_text(input_path.read_text(encoding="utf-8"), encoding="utf-8")
                result["backup_path"] = str(backup_path)
                result["migration_notes"].append(f"Created backup: {backup_path}")
            
            # Save migrated configuration
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                if output_path.suffix.lower() in [".yaml", ".yml"]:
                    yaml.dump(migrated_config, f, default_flow_style=False, indent=2)
                elif output_path.suffix.lower() == ".json":
                    json.dump(migrated_config, f, indent=2)
            
            result["success"] = True
            result["migration_notes"].append(f"Configuration saved to: {output_path}")
            
        except Exception as e:
            result["errors"].append(f"Migration failed: {e}")
            logger.error(f"Configuration migration failed: {e}")
        
        return result
    
    def detect_backend_compatibility(self) -> Dict[str, Any]:
        """Detect which LLM backends are available on the system.
        
        Returns:
            Dictionary with backend availability information
        """
        compatibility = {
            "ollama": {
                "available": False,
                "server_running": False,
                "base_url": "http://localhost:11434",
                "error": None
            },
            "llama_cpp": {
                "available": False,
                "error": None
            }
        }
        
        # Check Ollama availability
        try:
            from ..core.ollama_client import OllamaClient
            client = OllamaClient()
            compatibility["ollama"]["available"] = True
            compatibility["ollama"]["server_running"] = client.is_available()
        except ImportError as e:
            compatibility["ollama"]["error"] = f"Ollama client not available: {e}"
        except Exception as e:
            compatibility["ollama"]["error"] = f"Ollama check failed: {e}"
        
        # Check llama-cpp-python availability
        try:
            import llama_cpp
            compatibility["llama_cpp"]["available"] = True
        except ImportError as e:
            compatibility["llama_cpp"]["error"] = f"llama-cpp-python not installed: {e}"
        except Exception as e:
            compatibility["llama_cpp"]["error"] = f"llama-cpp-python check failed: {e}"
        
        return compatibility
    
    def recommend_backend(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Recommend the best backend based on system compatibility and configuration.
        
        Args:
            config: Optional configuration to consider
            
        Returns:
            Recommendation dictionary
        """
        compatibility = self.detect_backend_compatibility()
        
        recommendation = {
            "recommended_backend": "auto",
            "reasoning": [],
            "alternatives": [],
            "warnings": []
        }
        
        # Check if user has existing model files
        has_gguf_models = False
        if config:
            model_path = config.get("model", {}).get("path") or config.get("llm", {}).get("llama_cpp", {}).get("model_path")
            if model_path:
                model_path = Path(model_path).expanduser()
                has_gguf_models = model_path.exists() and model_path.suffix.lower() == ".gguf"
        
        # Recommendation logic
        if compatibility["ollama"]["available"] and compatibility["ollama"]["server_running"]:
            recommendation["recommended_backend"] = "ollama"
            recommendation["reasoning"].append("Ollama server is running and available")
            recommendation["reasoning"].append("Ollama provides easier model management and better performance")
            
            if has_gguf_models:
                recommendation["alternatives"].append("llama-cpp (to use existing GGUF models)")
                recommendation["reasoning"].append("Note: You have existing GGUF models that work with llama-cpp backend")
        
        elif compatibility["llama_cpp"]["available"] and has_gguf_models:
            recommendation["recommended_backend"] = "llama-cpp"
            recommendation["reasoning"].append("llama-cpp-python is available")
            recommendation["reasoning"].append("You have existing GGUF model files")
            
            if compatibility["ollama"]["available"]:
                recommendation["alternatives"].append("ollama (for easier model management)")
                recommendation["warnings"].append("Consider installing Ollama for better user experience")
        
        elif compatibility["ollama"]["available"]:
            recommendation["recommended_backend"] = "ollama"
            recommendation["reasoning"].append("Ollama is available (server not running)")
            recommendation["warnings"].append("Start Ollama server with: ollama serve")
        
        elif compatibility["llama_cpp"]["available"]:
            recommendation["recommended_backend"] = "llama-cpp"
            recommendation["reasoning"].append("llama-cpp-python is available")
            recommendation["warnings"].append("You'll need to download GGUF model files manually")
        
        else:
            recommendation["recommended_backend"] = "none"
            recommendation["reasoning"].append("No compatible backends found")
            recommendation["warnings"].append("Install either Ollama or llama-cpp-python to use LLM features")
        
        return recommendation


def migrate_config_cli(input_path: str, 
                      output_path: Optional[str] = None,
                      backup: bool = True,
                      verbose: bool = False) -> None:
    """CLI function for migrating configuration files.
    
    Args:
        input_path: Path to input configuration file
        output_path: Path for output file (optional)
        backup: Whether to create a backup
        verbose: Enable verbose output
    """
    migrator = ConfigMigrator()
    
    if verbose:
        print(f"Migrating configuration: {input_path}")
        
        # Show backend compatibility
        compatibility = migrator.detect_backend_compatibility()
        print("\nBackend Compatibility:")
        for backend, info in compatibility.items():
            status = "✓" if info["available"] else "✗"
            print(f"  {status} {backend}: {'Available' if info['available'] else info.get('error', 'Not available')}")
        
        # Show recommendation
        recommendation = migrator.recommend_backend()
        print(f"\nRecommended backend: {recommendation['recommended_backend']}")
        for reason in recommendation["reasoning"]:
            print(f"  - {reason}")
    
    # Perform migration
    result = migrator.migrate_config_file(input_path, output_path, backup)
    
    if result["success"]:
        print(f"✓ Migration successful!")
        if result["backup_path"]:
            print(f"  Backup created: {result['backup_path']}")
        print(f"  Output saved to: {result['output_path']}")
        
        if verbose:
            print("\nMigration notes:")
            for note in result["migration_notes"]:
                print(f"  - {note}")
    else:
        print(f"✗ Migration failed!")
        for error in result["errors"]:
            print(f"  Error: {error}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate LawFirm-RAG configuration files")
    parser.add_argument("input", help="Input configuration file path")
    parser.add_argument("-o", "--output", help="Output configuration file path")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backup of original file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    migrate_config_cli(
        input_path=args.input,
        output_path=args.output,
        backup=not args.no_backup,
        verbose=args.verbose
    ) 