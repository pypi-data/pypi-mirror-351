"""
LawFirm-RAG: AI-Powered Legal Document Analysis Package

A modern Python package for legal document analysis, query generation,
and AI-powered legal research assistance.
"""

__version__ = "0.1.0"
__author__ = "LawFirm-RAG Team"
__email__ = "contact@lawfirm-rag.com"

from .core.document_processor import DocumentProcessor
from .core.ai_engine import AIEngine
from .core.query_generator import QueryGenerator

__all__ = [
    "DocumentProcessor",
    "AIEngine", 
    "QueryGenerator",
] 