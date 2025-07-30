"""
Model downloader for LawFirm-RAG.

Simplified to work with Ollama's native model management.
"""

import logging
from typing import Dict, List, Optional
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class ModelDownloader:
    """Manages model downloading and availability through Ollama."""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize the model downloader.
        
        Args:
            base_url: Ollama server URL (optional, defaults to http://localhost:11434)
        """
        # Only pass base_url if it's actually provided and looks like a URL
        if base_url and base_url.startswith(('http://', 'https://')):
            self.ollama_client = OllamaClient(base_url=base_url)
        else:
            self.ollama_client = OllamaClient()  # Use default URL
        
        # Track download state
        self._current_download = {
            "model_variant": None,
            "status": "idle",
            "progress": 0.0,
            "error": None
        }
        
        # Recommended models for different use cases
        self.recommended_models = {
            "chat": {
                "name": "llama3.2:latest",
                "description": "General purpose chat model",
                "size": "2.0GB",
                "use_case": "General conversation and text generation"
            },
            "legal_analysis": {
                "name": "law-chat:latest",
                "description": "Legal-specific chat model",
                "size": "3.8GB", 
                "use_case": "Legal document analysis and legal Q&A"
            },
            "query_generation": {
                "name": "llama3.2:latest",
                "description": "Query generation model",
                "size": "2.0GB",
                "use_case": "Generating search queries for legal databases"
            },
            "embeddings": {
                "name": "mxbai-embed-large:latest",
                "description": "Text embedding model",
                "size": "669MB",
                "use_case": "Document similarity and semantic search"
            },
            "fallback": {
                "name": "llama3.2:latest",
                "description": "Fallback model",
                "size": "2.0GB",
                "use_case": "Backup model when primary models fail"
            }
        }
    
    def list_available_models(self) -> Dict[str, Dict]:
        """List all available models with their status.
        
        Returns:
            Dictionary mapping model names to their information and status
        """
        result = {}
        
        try:
            if not self.ollama_client.is_available():
                logger.warning("Ollama server not available")
                # Return recommended models with downloaded=False
                for model_type, info in self.recommended_models.items():
                    result[info["name"]] = {
                        **info,
                        "type": model_type,
                        "downloaded": False,
                        "available": False
                    }
                return result
            
            # Get models currently available in Ollama
            ollama_models = self.ollama_client.list_models()
            available_model_names = [model["name"] for model in ollama_models]
            
            # Add recommended models with their status
            for model_type, info in self.recommended_models.items():
                model_name = info["name"]
                is_available = model_name in available_model_names
                
                result[model_name] = {
                    **info,
                    "type": model_type,
                    "downloaded": is_available,
                    "available": is_available
                }
            
            # Add any other models found in Ollama that aren't in our recommended list
            for model in ollama_models:
                model_name = model["name"]
                if model_name not in result:
                    result[model_name] = {
                        "name": model_name,
                        "description": "Available in Ollama",
                        "size": model.get("size", "Unknown"),
                        "use_case": "General purpose",
                        "type": "other",
                        "downloaded": True,
                        "available": True
                    }
        
        except Exception as e:
            logger.error(f"Error listing available models: {e}")
        
        return result
    
    def download_model(self, model_name: str) -> bool:
        """Download a model using Ollama.
        
        Args:
            model_name: Name of the model to download
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            if not self.ollama_client.is_available():
                logger.error("Ollama server not available. Please start Ollama first.")
                self._current_download["error"] = "Ollama server not available"
                return False
            
            # Update download state
            self._current_download.update({
                "model_variant": model_name,
                "status": "downloading",
                "progress": 0.0,
                "error": None
            })
            
            logger.info(f"Downloading model: {model_name}")
            success = self.ollama_client.ensure_model_available(model_name)
            
            # Update final state
            if success:
                self._current_download.update({
                    "status": "completed",
                    "progress": 100.0
                })
            else:
                self._current_download.update({
                    "status": "failed",
                    "error": "Download failed"
                })
            
            return success
            
        except Exception as e:
            logger.error(f"Error downloading model {model_name}: {e}")
            self._current_download.update({
                "status": "failed",
                "error": str(e)
            })
            return False
    
    def download_recommended_models(self, model_types: Optional[List[str]] = None) -> Dict[str, bool]:
        """Download recommended models for specified types.
        
        Args:
            model_types: List of model types to download (None for all)
            
        Returns:
            Dictionary mapping model types to download success status
        """
        if model_types is None:
            model_types = list(self.recommended_models.keys())
        
        results = {}
        
        for model_type in model_types:
            if model_type not in self.recommended_models:
                logger.warning(f"Unknown model type: {model_type}")
                results[model_type] = False
                continue
            
            model_name = self.recommended_models[model_type]["name"]
            success = self.download_model(model_name)
            results[model_type] = success
            
            if success:
                logger.info(f"✓ Downloaded {model_type} model: {model_name}")
            else:
                logger.error(f"✗ Failed to download {model_type} model: {model_name}")
        
        return results
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary or None if not found
        """
        available_models = self.list_available_models()
        return available_models.get(model_name)
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available in Ollama.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model is available, False otherwise
        """
        try:
            if not self.ollama_client.is_available():
                return False
            
            available_models = self.ollama_client.list_models()
            model_names = [model["name"] for model in available_models]
            return model_name in model_names
            
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    def get_recommended_models(self) -> Dict[str, Dict]:
        """Get the recommended models configuration.
        
        Returns:
            Dictionary of recommended models
        """
        return self.recommended_models.copy()

    def get_download_progress(self) -> Dict[str, any]:
        """Get download progress for the current download."""
        return {
            "model_variant": self._current_download["model_variant"],
            "progress": self._current_download["progress"],
            "status": self._current_download["status"],
            "error": self._current_download["error"],
            "total_size": 0,  # Ollama doesn't provide size info easily
            "downloaded_size": 0,
            "speed": 0.0,
            "eta": None
        }
    
    def is_model_downloaded(self, model_name: str) -> bool:
        """Check if model exists in Ollama."""
        try:
            return model_name in [m["name"] for m in self.ollama_client.list_models()]
        except Exception:
            return False
    
    def cancel_download(self) -> bool:
        """Cancel download (reset state for Ollama)."""
        self._current_download.update({
            "model_variant": None,
            "status": "idle",
            "progress": 0.0,
            "error": None
        })
        return True
    
    def cleanup_failed_downloads(self) -> int:
        """Cleanup failed downloads (not applicable for Ollama but needed for API compatibility)."""
        return 0


def download_model(model_name: str) -> bool:
    """Convenience function to download a model.
    
    Args:
        model_name: Name of the model to download
        
    Returns:
        True if download successful, False otherwise
    """
    downloader = ModelDownloader()
    return downloader.download_model(model_name)


def list_available_models() -> Dict[str, Dict]:
    """Convenience function to list available models.
    
    Returns:
        Dictionary of available models
    """
    downloader = ModelDownloader()
    return downloader.list_available_models()


if __name__ == "__main__":
    # Simple CLI interface
    downloader = ModelDownloader()
    
    print("Available models:")
    models = downloader.list_available_models()
    
    for name, info in models.items():
        status = "✓ Downloaded" if info["downloaded"] else "○ Not downloaded"
        print(f"  {status} {name} - {info['description']} ({info['size']})")
    
    print("\nTo download a model, use:")
    print("  python -c \"from lawfirm_rag.core.model_downloader import download_model; download_model('llama3.2')\"")
    print("\nOr use the setup utility:")
    print("  python -c \"from lawfirm_rag.utils.setup import quick_setup; quick_setup()\"") 