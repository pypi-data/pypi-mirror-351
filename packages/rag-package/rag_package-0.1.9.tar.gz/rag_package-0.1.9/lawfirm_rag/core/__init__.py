"""
Core module for LawFirm-RAG package.

Contains the main business logic for document processing, AI engine,
query generation, and storage management.
"""

from .model_downloader import ModelDownloader
from .model_manager import ModelManager

__all__ = ['ModelDownloader', 'ModelManager'] 