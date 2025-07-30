"""
Setup utilities for LawFirm-RAG.

Provides easy setup functions for downloading and configuring models.
"""

import logging
from typing import Dict, List, Optional
from ..core.ollama_client import OllamaClient
from ..utils.config import get_config_manager, get_model_name

logger = logging.getLogger(__name__)


class SetupManager:
    """Manages setup and configuration of LawFirm-RAG."""
    
    def __init__(self):
        """Initialize the setup manager."""
        self.ollama_client = OllamaClient()
        self.config_manager = get_config_manager()
    
    def check_ollama_status(self) -> Dict[str, any]:
        """Check if Ollama is available and running.
        
        Returns:
            Status dictionary with availability and model information
        """
        status = {
            "ollama_available": False,
            "ollama_running": False,
            "models_available": [],
            "recommended_models": {},
            "missing_models": []
        }
        
        try:
            # Check if Ollama client is available
            status["ollama_available"] = True
            
            # Check if server is running
            if self.ollama_client.is_available():
                status["ollama_running"] = True
                
                # Get available models
                models = self.ollama_client.list_models()
                status["models_available"] = [model["name"] for model in models]
                
                # Get recommended models
                status["recommended_models"] = self.ollama_client.get_recommended_models()
                
                # Check which recommended models are missing
                for model_type, model_name in status["recommended_models"].items():
                    if model_name not in status["models_available"]:
                        status["missing_models"].append({
                            "type": model_type,
                            "name": model_name
                        })
            
        except Exception as e:
            logger.error(f"Error checking Ollama status: {e}")
        
        return status
    
    def setup_recommended_models(self, model_types: Optional[List[str]] = None) -> Dict[str, bool]:
        """Download and setup recommended models.
        
        Args:
            model_types: List of model types to setup (None for all)
            
        Returns:
            Dictionary mapping model types to success status
        """
        if not self.ollama_client.is_available():
            logger.error("Ollama server is not running. Please start Ollama first.")
            return {}
        
        recommended = self.ollama_client.get_recommended_models()
        
        if model_types is None:
            model_types = list(recommended.keys())
        
        results = {}
        
        for model_type in model_types:
            if model_type not in recommended:
                logger.warning(f"Unknown model type: {model_type}")
                results[model_type] = False
                continue
            
            model_name = recommended[model_type]
            logger.info(f"Setting up {model_type} model: {model_name}")
            
            success = self.ollama_client.ensure_model_available(model_name)
            results[model_type] = success
            
            if success:
                # Update configuration to use this model
                self.config_manager.set_model_name(model_type, model_name)
                logger.info(f"✓ {model_type} model ({model_name}) ready")
            else:
                logger.error(f"✗ Failed to setup {model_type} model ({model_name})")
        
        return results
    
    def quick_setup(self) -> bool:
        """Perform a quick setup with essential models.
        
        Returns:
            True if setup was successful, False otherwise
        """
        logger.info("Starting quick setup for LawFirm-RAG...")
        
        # Check Ollama status
        status = self.check_ollama_status()
        
        if not status["ollama_available"]:
            logger.error("Ollama is not available. Please install Ollama first.")
            return False
        
        if not status["ollama_running"]:
            logger.error("Ollama server is not running. Please start Ollama with: ollama serve")
            return False
        
        # Setup essential models (chat and embeddings for basic functionality)
        essential_models = ["chat", "embeddings"]
        results = self.setup_recommended_models(essential_models)
        
        success = all(results.values())
        
        if success:
            logger.info("✓ Quick setup completed successfully!")
            logger.info("You can now use LawFirm-RAG for basic document analysis.")
            logger.info("To add legal-specific models, run: setup_recommended_models(['legal_analysis'])")
        else:
            logger.error("✗ Quick setup failed. Please check the logs above.")
        
        return success
    
    def print_setup_instructions(self) -> None:
        """Print setup instructions for the user."""
        print("\n" + "="*60)
        print("LawFirm-RAG Setup Instructions")
        print("="*60)
        
        status = self.check_ollama_status()
        
        if not status["ollama_available"]:
            print("\n1. Install Ollama:")
            print("   Visit: https://ollama.ai")
            print("   Download and install Ollama for your operating system")
            return
        
        if not status["ollama_running"]:
            print("\n1. Start Ollama server:")
            print("   Run: ollama serve")
            print("   (Keep this running in a separate terminal)")
            return
        
        print(f"\n✓ Ollama is running with {len(status['models_available'])} models")
        
        if status["missing_models"]:
            print(f"\n📥 Missing recommended models ({len(status['missing_models'])}):")
            for missing in status["missing_models"]:
                print(f"   - {missing['type']}: {missing['name']}")
            
            print("\n🚀 Quick setup commands:")
            print("   # Basic functionality (chat + embeddings)")
            print("   python -c \"from lawfirm_rag.utils.setup import SetupManager; SetupManager().quick_setup()\"")
            print("\n   # Or manually pull models:")
            for missing in status["missing_models"]:
                print(f"   ollama pull {missing['name']}")
        else:
            print("\n✓ All recommended models are available!")
            print("✓ LawFirm-RAG is ready to use!")


def quick_setup() -> bool:
    """Convenience function for quick setup."""
    return SetupManager().quick_setup()


def print_setup_instructions() -> None:
    """Convenience function to print setup instructions."""
    SetupManager().print_setup_instructions()


if __name__ == "__main__":
    print_setup_instructions() 