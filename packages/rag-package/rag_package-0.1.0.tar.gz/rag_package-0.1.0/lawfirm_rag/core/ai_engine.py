"""
AI Engine module for LawFirm-RAG.

Handles GGUF model loading, inference, and AI-powered analysis.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)


class AIEngine:
    """Handles AI model operations and inference."""
    
    def __init__(self, model_path: Optional[str] = None, **model_kwargs):
        """Initialize the AI engine.
        
        Args:
            model_path: Path to the GGUF model file.
            **model_kwargs: Additional arguments for model initialization.
        """
        self.model_path = model_path
        self.model = None
        self.model_kwargs = model_kwargs
        self.is_loaded = False
        
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """Load the GGUF model.
        
        Args:
            model_path: Path to the model file. If None, uses instance model_path.
            
        Returns:
            True if model loaded successfully, False otherwise.
        """
        if Llama is None:
            logger.error("llama-cpp-python is not installed. Install with: pip install llama-cpp-python")
            return False
            
        if model_path:
            self.model_path = model_path
            
        if not self.model_path:
            logger.error("No model path specified")
            return False
            
        model_file = Path(self.model_path)
        if not model_file.exists():
            logger.error(f"Model file not found: {self.model_path}")
            return False
            
        try:
            logger.info(f"Loading model from: {self.model_path}")
            
            # Default model parameters optimized for legal text
            default_kwargs = {
                "n_ctx": 4096,  # Context window
                "n_batch": 512,  # Batch size
                "verbose": False,
                "n_threads": None,  # Use all available threads
            }
            
            # Merge with user-provided kwargs
            model_kwargs = {**default_kwargs, **self.model_kwargs}
            
            self.model = Llama(model_path=self.model_path, **model_kwargs)
            self.is_loaded = True
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
            self.is_loaded = False
            return False
            
    def generate_response(self, prompt: str, max_tokens: int = 1000, 
                         temperature: float = 0.7, **kwargs) -> str:
        """Generate a response using the loaded model.
        
        Args:
            prompt: Input prompt for the model.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = random).
            **kwargs: Additional generation parameters.
            
        Returns:
            Generated response text.
            
        Raises:
            RuntimeError: If model is not loaded.
        """
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Model is not loaded. Call load_model() first.")
            
        try:
            # Default generation parameters
            generation_kwargs = {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,
                "stop": ["</s>", "\n\n"],
                **kwargs
            }
            
            response = self.model(prompt, **generation_kwargs)
            
            # Extract text from response
            if isinstance(response, dict) and "choices" in response:
                text = response["choices"][0]["text"].strip()
            else:
                text = str(response).strip()
            
            # Clean up chat format artifacts
            text = self._clean_response(text)
            return text
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
            
    def analyze_document(self, text: str, analysis_type: str = "summary") -> str:
        """Analyze a document using the AI model.
        
        Args:
            text: Document text to analyze.
            analysis_type: Type of analysis ("summary", "key_points", "legal_issues").
            
        Returns:
            Analysis result.
        """
        if analysis_type == "summary":
            prompt = self._create_summary_prompt(text)
        elif analysis_type == "key_points":
            prompt = self._create_key_points_prompt(text)
        elif analysis_type == "legal_issues":
            prompt = self._create_legal_issues_prompt(text)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
            
        return self.generate_response(prompt, max_tokens=1500, temperature=0.3)
        
    def generate_search_query(self, text: str, database: str = "westlaw") -> str:
        """Generate a search query for legal databases.
        
        Args:
            text: Document text to base the query on.
            database: Target database ("westlaw", "lexisnexis", "casetext").
            
        Returns:
            Generated search query.
        """
        prompt = self._create_search_query_prompt(text, database)
        return self.generate_response(prompt, max_tokens=200, temperature=0.2)
        
    def _create_summary_prompt(self, text: str) -> str:
        """Create a prompt for document summarization."""
        return f"""You are a legal AI assistant. Please provide a concise summary of the following legal document. Focus on the key legal issues, parties involved, and main arguments.

Document:
{text[:3000]}  # Limit text to avoid context overflow

Summary:"""

    def _create_key_points_prompt(self, text: str) -> str:
        """Create a prompt for extracting key points."""
        return f"""You are a legal AI assistant. Please extract the key legal points from the following document. List them as bullet points.

Document:
{text[:3000]}

Key Legal Points:
•"""

    def _create_legal_issues_prompt(self, text: str) -> str:
        """Create a prompt for identifying legal issues."""
        return f"""You are a legal AI assistant. Please identify the main legal issues and relevant areas of law in the following document.

Document:
{text[:3000]}

Legal Issues and Areas of Law:"""

    def _create_search_query_prompt(self, text: str, database: str) -> str:
        """Create a prompt for generating search queries."""
        if database == "westlaw":
            return f"""You are a legal research expert. Create a Westlaw search query using Terms and Connectors syntax.

WESTLAW SYNTAX RULES:
- Use & for AND (required terms)
- Use | for OR (alternative terms) 
- Use /s for same sentence proximity
- Use /p for same paragraph proximity
- Use /n for within n words (e.g., /3 for within 3 words)
- Use ! for truncation (negligen! finds negligent, negligence, etc.)
- Use % for single character wildcard
- Put phrases in quotes: "personal injury"
- Use parentheses for grouping: (contract | agreement) & breach

REALISTIC WESTLAW EXAMPLES:
- negligen! /p "motor vehicle" /s injur! & damag!
- (contract | agreement) /s breach /p (remedy | damag!)
- "personal injury" /p automobile /s insurance /3 claim!
- liabil! /s (product! | manufactur!) & defect! /p injur!

Document excerpt:
{text[:2000]}

Create a precise Westlaw Terms and Connectors query using proximity operators and truncation (respond with ONLY the query, no explanations):"""
        
        elif database == "lexisnexis":
            return f"""Create a LexisNexis search query using boolean operators AND, OR, NOT.

Document excerpt:
{text[:2000]}

Generate a precise LexisNexis query (respond with ONLY the query):"""
        
        else:  # casetext or other
            return f"""Create a search query for {database} using natural language and boolean operators.

Document excerpt:
{text[:2000]}

Generate a precise search query (respond with ONLY the query):"""

    def _clean_response(self, text: str) -> str:
        """Clean up model response by removing chat format artifacts.
        
        Args:
            text: Raw model response text.
            
        Returns:
            Cleaned response text.
        """
        # Remove common chat format tags
        text = text.replace("[/INST]", "").replace("[INST]", "")
        text = text.replace("<s>", "").replace("</s>", "")
        text = text.replace("Assistant:", "").replace("Human:", "")
        
        # Remove leading/trailing whitespace and newlines
        text = text.strip()
        
        # Remove any leading colons or dashes that might be artifacts
        while text.startswith(":") or text.startswith("-") or text.startswith("*"):
            text = text[1:].strip()
            
        return text

    def unload_model(self) -> None:
        """Unload the model to free memory."""
        if self.model:
            del self.model
            self.model = None
            self.is_loaded = False
            logger.info("Model unloaded")
            
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.unload_model() 