"""
Model Downloader for Hugging Face GGUF Models

This module provides functionality to download AI models from Hugging Face,
specifically designed for GGUF format models used in legal document analysis.
"""

import os
import hashlib
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Generator, Tuple
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)


class ModelDownloadError(Exception):
    """Custom exception for model download errors"""
    pass


class ModelDownloader:
    """
    Handles downloading and managing AI models from Hugging Face.
    
    Supports downloading GGUF models with progress tracking, validation,
    and proper error handling.
    """
    
    # Hugging Face model repository and supported variants
    HF_REPO = "TheBloke/law-chat-GGUF"
    SUPPORTED_VARIANTS = {
        "law-chat-q2_k": "law-chat.Q2_K.gguf",
        "law-chat-q3_k_m": "law-chat.Q3_K_M.gguf", 
        "law-chat-q4_0": "law-chat.Q4_0.gguf",
        "law-chat-q5_0": "law-chat.Q5_0.gguf",
        "law-chat-q8_0": "law-chat.Q8_0.gguf"
    }
    
    # Expected file sizes (in bytes) for validation
    EXPECTED_SIZES = {
        "law-chat-q2_k": 2_830_000_000,    # ~2.83 GB
        "law-chat-q3_k_m": 3_300_000_000,  # ~3.30 GB
        "law-chat-q4_0": 3_830_000_000,    # ~3.83 GB
        "law-chat-q5_0": 4_650_000_000,    # ~4.65 GB
        "law-chat-q8_0": 7_160_000_000     # ~7.16 GB
    }
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the ModelDownloader.
        
        Args:
            storage_dir: Directory to store downloaded models. 
                        Defaults to ./models/downloaded/
        """
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent / "models" / "downloaded"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Track current download progress
        self._current_download = {
            "model_variant": None,
            "progress": 0.0,
            "status": "idle",
            "error": None,
            "total_size": 0,
            "downloaded_size": 0,
            "speed": 0.0,
            "eta": None
        }
    
    def get_download_url(self, model_variant: str) -> str:
        """
        Generate the correct Hugging Face download URL for a model variant.
        
        Args:
            model_variant: The model variant identifier (e.g., 'law-chat-q4_0')
            
        Returns:
            The complete download URL
            
        Raises:
            ModelDownloadError: If the model variant is not supported
        """
        if model_variant not in self.SUPPORTED_VARIANTS:
            raise ModelDownloadError(
                f"Unsupported model variant: {model_variant}. "
                f"Supported variants: {list(self.SUPPORTED_VARIANTS.keys())}"
            )
        
        filename = self.SUPPORTED_VARIANTS[model_variant]
        url = f"https://huggingface.co/{self.HF_REPO}/resolve/main/{filename}?download=true"
        
        logger.info(f"Generated download URL for {model_variant}: {url}")
        return url
    
    def get_model_path(self, model_variant: str) -> Path:
        """Get the local file path where a model should be stored."""
        filename = self.SUPPORTED_VARIANTS[model_variant]
        return self.storage_dir / filename
    
    def is_model_downloaded(self, model_variant: str) -> bool:
        """Check if a model is already downloaded and valid."""
        model_path = self.get_model_path(model_variant)
        if not model_path.exists():
            return False
        
        # Quick size validation
        expected_size = self.EXPECTED_SIZES.get(model_variant)
        if expected_size:
            actual_size = model_path.stat().st_size
            # Allow 5% variance in file size
            size_diff = abs(actual_size - expected_size) / expected_size
            if size_diff > 0.05:
                logger.warning(
                    f"Model {model_variant} size mismatch. "
                    f"Expected: {expected_size}, Actual: {actual_size}"
                )
                return False
        
        return True
    
    def track_progress(self, response: requests.Response, model_variant: str) -> Generator[Dict, None, None]:
        """
        Generator that tracks download progress and yields progress updates.
        
        Args:
            response: The requests response object
            model_variant: The model variant being downloaded
            
        Yields:
            Dictionary containing progress information
        """
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        start_time = time.time()
        
        self._current_download.update({
            "model_variant": model_variant,
            "status": "downloading",
            "total_size": total_size,
            "downloaded_size": 0,
            "progress": 0.0,
            "error": None
        })
        
        chunk_size = 8192  # 8KB chunks
        last_update_time = start_time
        
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                downloaded_size += len(chunk)
                current_time = time.time()
                
                # Update progress every 0.5 seconds to avoid too frequent updates
                if current_time - last_update_time >= 0.5:
                    elapsed_time = current_time - start_time
                    speed = downloaded_size / elapsed_time if elapsed_time > 0 else 0
                    
                    progress = (downloaded_size / total_size * 100) if total_size > 0 else 0
                    eta = (total_size - downloaded_size) / speed if speed > 0 else None
                    
                    self._current_download.update({
                        "downloaded_size": downloaded_size,
                        "progress": progress,
                        "speed": speed,
                        "eta": eta
                    })
                    
                    last_update_time = current_time
                    
                    yield {
                        "progress": progress,
                        "downloaded_size": downloaded_size,
                        "total_size": total_size,
                        "speed": speed,
                        "eta": eta,
                        "status": "downloading"
                    }
                
                yield chunk
    
    def validate_downloaded_file(self, file_path: Path, model_variant: str) -> bool:
        """
        Validate a downloaded model file.
        
        Args:
            file_path: Path to the downloaded file
            model_variant: The model variant identifier
            
        Returns:
            True if the file is valid, False otherwise
        """
        if not file_path.exists():
            logger.error(f"Downloaded file does not exist: {file_path}")
            return False
        
        # Check file size
        actual_size = file_path.stat().st_size
        expected_size = self.EXPECTED_SIZES.get(model_variant)
        
        if expected_size:
            size_diff = abs(actual_size - expected_size) / expected_size
            if size_diff > 0.05:  # Allow 5% variance
                logger.error(
                    f"File size validation failed for {model_variant}. "
                    f"Expected: {expected_size}, Actual: {actual_size}"
                )
                return False
        
        # Check if file is not empty and has reasonable content
        if actual_size < 1000:  # Less than 1KB is definitely wrong
            logger.error(f"Downloaded file is too small: {actual_size} bytes")
            return False
        
        # Basic GGUF file format validation (check magic bytes)
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                if magic != b'GGUF':
                    logger.error(f"Invalid GGUF file format. Magic bytes: {magic}")
                    return False
        except Exception as e:
            logger.error(f"Error reading file for validation: {e}")
            return False
        
        logger.info(f"File validation successful for {model_variant}")
        return True
    
    def download_model(self, model_variant: str, force: bool = False) -> bool:
        """
        Download a model from Hugging Face.
        
        Args:
            model_variant: The model variant to download
            force: If True, re-download even if file exists
            
        Returns:
            True if download was successful, False otherwise
            
        Raises:
            ModelDownloadError: If download fails
        """
        if model_variant not in self.SUPPORTED_VARIANTS:
            raise ModelDownloadError(f"Unsupported model variant: {model_variant}")
        
        model_path = self.get_model_path(model_variant)
        
        # Check if already downloaded and valid
        if not force and self.is_model_downloaded(model_variant):
            logger.info(f"Model {model_variant} already downloaded and valid")
            self._current_download["status"] = "completed"
            return True
        
        # Start download
        logger.info(f"Starting download of {model_variant}")
        url = self.get_download_url(model_variant)
        
        try:
            # Create a session for better connection handling
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'LawFirm-RAG/1.0.0 (https://github.com/lawfirm-rag/lawfirm-rag)'
            })
            
            # Start the download with streaming
            response = session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            temp_path = model_path.with_suffix('.tmp')
            
            with open(temp_path, 'wb') as f:
                for chunk in self.track_progress(response, model_variant):
                    if isinstance(chunk, bytes):
                        f.write(chunk)
            
            # Validate the downloaded file
            if not self.validate_downloaded_file(temp_path, model_variant):
                temp_path.unlink(missing_ok=True)
                self._current_download["status"] = "error"
                self._current_download["error"] = "File validation failed"
                raise ModelDownloadError("Downloaded file validation failed")
            
            # Move temp file to final location
            temp_path.rename(model_path)
            
            self._current_download["status"] = "completed"
            self._current_download["progress"] = 100.0
            
            logger.info(f"Successfully downloaded {model_variant} to {model_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error downloading {model_variant}: {e}"
            logger.error(error_msg)
            self._current_download["status"] = "error"
            self._current_download["error"] = error_msg
            raise ModelDownloadError(error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error downloading {model_variant}: {e}"
            logger.error(error_msg)
            self._current_download["status"] = "error"
            self._current_download["error"] = error_msg
            raise ModelDownloadError(error_msg)
    
    def get_download_progress(self) -> Dict:
        """Get the current download progress information."""
        return self._current_download.copy()
    
    def cancel_download(self) -> bool:
        """
        Cancel the current download.
        
        Returns:
            True if cancellation was successful
        """
        if self._current_download["status"] == "downloading":
            self._current_download["status"] = "cancelled"
            logger.info("Download cancelled by user")
            return True
        return False
    
    def list_available_models(self) -> Dict[str, Dict]:
        """
        List all available model variants with their information.
        
        Returns:
            Dictionary mapping variant names to their information
        """
        models = {}
        for variant, filename in self.SUPPORTED_VARIANTS.items():
            models[variant] = {
                "filename": filename,
                "size": self.EXPECTED_SIZES.get(variant, 0),
                "downloaded": self.is_model_downloaded(variant),
                "path": str(self.get_model_path(variant))
            }
        return models
    
    def cleanup_failed_downloads(self) -> int:
        """
        Clean up any temporary or corrupted download files.
        
        Returns:
            Number of files cleaned up
        """
        cleaned = 0
        for file_path in self.storage_dir.glob("*.tmp"):
            try:
                file_path.unlink()
                cleaned += 1
                logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up {file_path}: {e}")
        
        return cleaned 