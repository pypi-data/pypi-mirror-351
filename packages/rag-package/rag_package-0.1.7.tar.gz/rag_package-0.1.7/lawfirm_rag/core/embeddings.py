"""
Local Embedding System using sentence-transformers

This module provides efficient local embedding generation with support for:
- Multiple embedding models (all-MiniLM-L12-v2, BGE, etc.)
- Batch processing for large document collections
- Caching for improved performance
- Memory-efficient processing
"""

import os
import pickle
import hashlib
import logging
from typing import List, Dict, Optional, Union, Tuple
from pathlib import Path
import numpy as np

# PyTorch version compatibility check
try:
    import torch
    # Check if get_default_device is available (PyTorch >= 2.0)
    if not hasattr(torch, 'get_default_device'):
        # Add compatibility shim for older PyTorch versions
        def get_default_device():
            return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        torch.get_default_device = get_default_device
        logger = logging.getLogger(__name__)
        logger.warning("Applied PyTorch compatibility shim for get_default_device")
except ImportError:
    pass

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

logger = logging.getLogger(__name__)


class EmbeddingConfig:
    """Configuration for different embedding models."""
    
    MODELS = {
        "all-MiniLM-L12-v2": {
            "name": "sentence-transformers/all-MiniLM-L12-v2",
            "dimensions": 384,
            "max_sequence": 512,
            "size_mb": 120,
            "description": "Balanced performance and quality, good for general use",
            "recommended_for": ["legal", "business", "general"]
        },
        "all-MiniLM-L6-v2": {
            "name": "sentence-transformers/all-MiniLM-L6-v2", 
            "dimensions": 384,
            "max_sequence": 512,
            "size_mb": 80,
            "description": "Faster, smaller model with good performance",
            "recommended_for": ["general", "quick_processing"]
        },
        "bge-small-en-v1.5": {
            "name": "BAAI/bge-small-en-v1.5",
            "dimensions": 384,
            "max_sequence": 512,
            "size_mb": 130,
            "description": "High quality embeddings, excellent for retrieval",
            "recommended_for": ["legal", "academic", "high_quality"]
        },
        "bge-base-en-v1.5": {
            "name": "BAAI/bge-base-en-v1.5",
            "dimensions": 768,
            "max_sequence": 512,
            "size_mb": 440,
            "description": "Larger model with higher dimensions, best quality",
            "recommended_for": ["academic", "research", "best_quality"]
        }
    }
    
    @classmethod
    def get_default_model(cls, use_case: str = "general") -> str:
        """Get the default model for a specific use case."""
        defaults = {
            "legal": "all-MiniLM-L12-v2",
            "business": "all-MiniLM-L12-v2", 
            "academic": "bge-small-en-v1.5",
            "general": "all-MiniLM-L12-v2",
            "fast": "all-MiniLM-L6-v2",
            "quality": "bge-base-en-v1.5"
        }
        return defaults.get(use_case, "all-MiniLM-L12-v2")
    
    @classmethod
    def get_model_info(cls, model_key: str) -> Dict:
        """Get information about a specific model."""
        return cls.MODELS.get(model_key, cls.MODELS["all-MiniLM-L12-v2"])


class EmbeddingCache:
    """Simple file-based cache for embeddings."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.lawfirm-rag/embeddings_cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Embedding cache directory: {self.cache_dir}")
    
    def _get_cache_key(self, text: str, model_name: str) -> str:
        """Generate a cache key for text and model combination."""
        content = f"{model_name}:{text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, text: str, model_name: str) -> Optional[np.ndarray]:
        """Retrieve cached embedding if available."""
        cache_key = self._get_cache_key(text, model_name)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cached embedding: {e}")
                # Remove corrupted cache file
                cache_file.unlink(missing_ok=True)
        
        return None
    
    def set(self, text: str, model_name: str, embedding: np.ndarray) -> None:
        """Cache an embedding."""
        try:
            cache_key = self._get_cache_key(text, model_name)
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except Exception as e:
            logger.warning(f"Failed to cache embedding: {e}")
    
    def clear(self) -> None:
        """Clear the entire cache."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        logger.info("Embedding cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cached_embeddings": len(cache_files),
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir)
        }


class LocalEmbeddingGenerator:
    """High-performance local embedding generator using sentence-transformers."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L12-v2",
        cache_enabled: bool = True,
        cache_dir: Optional[str] = None,
        device: Optional[str] = None,
        batch_size: int = 32
    ):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the embedding model to use
            cache_enabled: Whether to enable embedding caching
            cache_dir: Directory for caching embeddings
            device: Device to run model on ('cpu', 'cuda', etc.)
            batch_size: Batch size for processing multiple texts
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for local embeddings. "
                "Install with: pip install sentence-transformers"
            )
        
        self.model_name = model_name
        self.model_config = EmbeddingConfig.get_model_info(model_name)
        self.batch_size = batch_size
        self.device = device
        
        # Initialize cache
        self.cache_enabled = cache_enabled
        self.cache = EmbeddingCache(cache_dir) if cache_enabled else None
        
        # Initialize model (lazy loading)
        self._model = None
        self._model_loaded = False
        
        logger.info(f"Initialized LocalEmbeddingGenerator with model: {model_name}")
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model."""
        if not self._model_loaded:
            try:
                logger.info(f"Loading embedding model: {self.model_config['name']}")
                self._model = SentenceTransformer(
                    self.model_config['name'],
                    device=self.device
                )
                self._model_loaded = True
                logger.info(f"Model loaded successfully. Dimensions: {self.dimensions}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        
        return self._model
    
    @property
    def dimensions(self) -> int:
        """Get the embedding dimensions."""
        return self.model_config['dimensions']
    
    @property
    def max_sequence_length(self) -> int:
        """Get the maximum sequence length."""
        return self.model_config['max_sequence']
    
    def embed_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.dimensions, dtype=np.float32)
        
        # Check cache first
        if self.cache_enabled:
            cached = self.cache.get(text, self.model_name)
            if cached is not None:
                return cached
        
        # Generate embedding
        try:
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True
            ).astype(np.float32)
            
            # Cache the result
            if self.cache_enabled:
                self.cache.set(text, self.model_name, embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            # Return zero vector as fallback
            return np.zeros(self.dimensions, dtype=np.float32)
    
    def embed_batch(
        self, 
        texts: List[str], 
        show_progress: bool = True
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            show_progress: Whether to show progress bar
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts and track indices
        valid_texts = []
        valid_indices = []
        
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)
        
        if not valid_texts:
            # Return zero vectors for all texts
            return [np.zeros(self.dimensions, dtype=np.float32) for _ in texts]
        
        # Check cache for valid texts
        embeddings_map = {}
        uncached_texts = []
        uncached_indices = []
        
        if self.cache_enabled:
            for i, text in enumerate(valid_texts):
                cached = self.cache.get(text, self.model_name)
                if cached is not None:
                    embeddings_map[i] = cached
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = valid_texts
            uncached_indices = list(range(len(valid_texts)))
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            try:
                logger.info(f"Generating embeddings for {len(uncached_texts)} texts")
                
                # Process in batches
                uncached_embeddings = self.model.encode(
                    uncached_texts,
                    batch_size=self.batch_size,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=show_progress
                ).astype(np.float32)
                
                # Store in map and cache
                for i, embedding in enumerate(uncached_embeddings):
                    idx = uncached_indices[i]
                    embeddings_map[idx] = embedding
                    
                    if self.cache_enabled:
                        self.cache.set(uncached_texts[i], self.model_name, embedding)
                        
            except Exception as e:
                logger.error(f"Failed to generate batch embeddings: {e}")
                # Fill with zero vectors
                for idx in uncached_indices:
                    embeddings_map[idx] = np.zeros(self.dimensions, dtype=np.float32)
        
        # Reconstruct full result list
        result = []
        valid_idx = 0
        
        for i in range(len(texts)):
            if i in valid_indices:
                result.append(embeddings_map[valid_idx])
                valid_idx += 1
            else:
                # Zero vector for empty/invalid text
                result.append(np.zeros(self.dimensions, dtype=np.float32))
        
        return result
    
    def get_model_info(self) -> Dict:
        """Get information about the current model."""
        info = self.model_config.copy()
        info.update({
            "current_model": self.model_name,
            "model_loaded": self._model_loaded,
            "cache_enabled": self.cache_enabled,
            "batch_size": self.batch_size,
            "device": str(self.device) if self.device else "auto"
        })
        
        if self.cache_enabled:
            info["cache_stats"] = self.cache.get_cache_stats()
            
        return info
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        if self.cache_enabled:
            self.cache.clear()
            logger.info("Embedding cache cleared")
    
    def warmup(self) -> None:
        """Warm up the model by generating a test embedding."""
        logger.info("Warming up embedding model...")
        test_text = "This is a test sentence for model warmup."
        self.embed_single(test_text)
        logger.info("Model warmup complete")


def get_available_models() -> Dict[str, Dict]:
    """Get information about all available embedding models."""
    return EmbeddingConfig.MODELS


def create_embedding_generator(
    model_name: Optional[str] = None,
    use_case: str = "general",
    **kwargs
) -> LocalEmbeddingGenerator:
    """
    Create an embedding generator with sensible defaults.
    
    Args:
        model_name: Specific model name, or None to auto-select
        use_case: Use case to optimize for if model_name is None
        **kwargs: Additional arguments for LocalEmbeddingGenerator
        
    Returns:
        Configured LocalEmbeddingGenerator instance
    """
    if model_name is None:
        model_name = EmbeddingConfig.get_default_model(use_case)
    
    return LocalEmbeddingGenerator(model_name=model_name, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    # Test the embedding system
    logging.basicConfig(level=logging.INFO)
    
    # Create generator
    generator = create_embedding_generator(use_case="legal")
    
    # Test single embedding
    text = "This is a legal document about contract law."
    embedding = generator.embed_single(text)
    print(f"Single embedding shape: {embedding.shape}")
    
    # Test batch embeddings
    texts = [
        "Contract law defines the enforceability of agreements.",
        "Tort law deals with civil wrongs and damages.",
        "Criminal law addresses offenses against society.",
        ""  # Test empty text handling
    ]
    
    embeddings = generator.embed_batch(texts)
    print(f"Batch embeddings: {len(embeddings)} vectors of shape {embeddings[0].shape}")
    
    # Show model info
    info = generator.get_model_info()
    print(f"Model info: {info}") 