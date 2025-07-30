"""
File handling utilities for LawFirm-RAG.

Provides utility functions for file operations, validation, and management.
"""

import os
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file operations and validation."""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    SUPPORTED_MIMETYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    }
    
    def __init__(self, max_file_size: int = 100 * 1024 * 1024):  # 100MB default
        """Initialize file handler.
        
        Args:
            max_file_size: Maximum file size in bytes.
        """
        self.max_file_size = max_file_size
        
    def validate_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Validate a file for processing.
        
        Args:
            file_path: Path to the file to validate.
            
        Returns:
            Dictionary with validation results.
        """
        file_path = Path(file_path)
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "file_info": {}
        }
        
        # Check if file exists
        if not file_path.exists():
            result["errors"].append(f"File does not exist: {file_path}")
            return result
            
        # Check if it's a file (not directory)
        if not file_path.is_file():
            result["errors"].append(f"Path is not a file: {file_path}")
            return result
            
        # Get file info
        try:
            stat = file_path.stat()
            result["file_info"] = {
                "name": file_path.name,
                "size": stat.st_size,
                "extension": file_path.suffix.lower(),
                "mime_type": mimetypes.guess_type(str(file_path))[0]
            }
        except Exception as e:
            result["errors"].append(f"Could not read file info: {e}")
            return result
            
        # Check file size
        if result["file_info"]["size"] > self.max_file_size:
            size_mb = result["file_info"]["size"] / (1024 * 1024)
            max_mb = self.max_file_size / (1024 * 1024)
            result["errors"].append(f"File too large: {size_mb:.1f}MB (max: {max_mb:.1f}MB)")
            
        # Check file extension
        if result["file_info"]["extension"] not in self.SUPPORTED_EXTENSIONS:
            result["errors"].append(
                f"Unsupported file extension: {result['file_info']['extension']}. "
                f"Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
            
        # Check MIME type if available
        mime_type = result["file_info"]["mime_type"]
        if mime_type and mime_type not in self.SUPPORTED_MIMETYPES:
            result["warnings"].append(f"Unexpected MIME type: {mime_type}")
            
        # Check if file is readable
        try:
            with open(file_path, 'rb') as f:
                f.read(1024)  # Try to read first 1KB
        except Exception as e:
            result["errors"].append(f"File is not readable: {e}")
            
        # Set valid flag
        result["valid"] = len(result["errors"]) == 0
        
        return result
        
    def validate_files(self, file_paths: List[Union[str, Path]]) -> Dict[str, Any]:
        """Validate multiple files.
        
        Args:
            file_paths: List of file paths to validate.
            
        Returns:
            Dictionary with validation results for all files.
        """
        results = {
            "valid_files": [],
            "invalid_files": [],
            "total_size": 0,
            "summary": {
                "total": len(file_paths),
                "valid": 0,
                "invalid": 0
            }
        }
        
        for file_path in file_paths:
            validation = self.validate_file(file_path)
            
            if validation["valid"]:
                results["valid_files"].append({
                    "path": str(file_path),
                    "info": validation["file_info"]
                })
                results["total_size"] += validation["file_info"]["size"]
                results["summary"]["valid"] += 1
            else:
                results["invalid_files"].append({
                    "path": str(file_path),
                    "errors": validation["errors"],
                    "warnings": validation["warnings"]
                })
                results["summary"]["invalid"] += 1
                
        return results
        
    def find_documents(self, directory: Union[str, Path], 
                      recursive: bool = False) -> List[Path]:
        """Find supported document files in a directory.
        
        Args:
            directory: Directory to search in.
            recursive: Whether to search recursively.
            
        Returns:
            List of found document file paths.
        """
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            logger.warning(f"Directory does not exist or is not a directory: {directory}")
            return []
            
        files = []
        
        try:
            if recursive:
                for ext in self.SUPPORTED_EXTENSIONS:
                    files.extend(directory.rglob(f"*{ext}"))
            else:
                for ext in self.SUPPORTED_EXTENSIONS:
                    files.extend(directory.glob(f"*{ext}"))
                    
        except Exception as e:
            logger.error(f"Error searching directory {directory}: {e}")
            
        return sorted(files)
        
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get detailed information about a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Dictionary with file information.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": "File does not exist"}
            
        try:
            stat = file_path.stat()
            
            return {
                "name": file_path.name,
                "stem": file_path.stem,
                "extension": file_path.suffix.lower(),
                "size": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "mime_type": mimetypes.guess_type(str(file_path))[0],
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "absolute_path": str(file_path.absolute()),
                "is_supported": file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
            }
            
        except Exception as e:
            return {"error": f"Could not read file info: {e}"}
            
    def safe_filename(self, filename: str) -> str:
        """Create a safe filename by removing/replacing problematic characters.
        
        Args:
            filename: Original filename.
            
        Returns:
            Safe filename.
        """
        # Remove or replace problematic characters
        unsafe_chars = '<>:"/\\|?*'
        safe_name = filename
        
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
            
        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip(' .')
        
        # Ensure it's not empty
        if not safe_name:
            safe_name = "unnamed_file"
            
        # Limit length
        if len(safe_name) > 255:
            name, ext = os.path.splitext(safe_name)
            safe_name = name[:255-len(ext)] + ext
            
        return safe_name
        
    def ensure_directory(self, directory: Union[str, Path]) -> Path:
        """Ensure a directory exists, creating it if necessary.
        
        Args:
            directory: Directory path.
            
        Returns:
            Path object for the directory.
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory
        
    def cleanup_temp_files(self, temp_dir: Union[str, Path], 
                          max_age_hours: int = 24) -> int:
        """Clean up old temporary files.
        
        Args:
            temp_dir: Temporary directory to clean.
            max_age_hours: Maximum age of files to keep in hours.
            
        Returns:
            Number of files cleaned up.
        """
        temp_dir = Path(temp_dir)
        
        if not temp_dir.exists():
            return 0
            
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        try:
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.debug(f"Cleaned up old temp file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Could not delete temp file {file_path}: {e}")
                            
        except Exception as e:
            logger.error(f"Error cleaning temp directory {temp_dir}: {e}")
            
        return cleaned_count 