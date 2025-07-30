"""
RAG: AI-Powered Legal Document Analysis Package

A modern Python package for legal document analysis, query generation,
and AI-powered legal research assistance.
"""

__version__ = "0.1.9"
__author__ = "dannymexe"
__email__ = "dannyjmargolin@gmail.com"

from .core.document_processor import DocumentProcessor
from .core.ai_engine import AIEngine
from .core.query_generator import QueryGenerator

__all__ = [
    "DocumentProcessor",
    "AIEngine", 
    "QueryGenerator",
] 