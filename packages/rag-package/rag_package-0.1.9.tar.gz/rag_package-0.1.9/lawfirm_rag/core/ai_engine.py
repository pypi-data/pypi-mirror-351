"""
AI Engine module for LawFirm-RAG.

Handles LLM operations using a unified abstraction layer that supports
both Ollama and llama-cpp-python backends.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import re

from .llm_backend import (
    LLMFactory, 
    LLMContext, 
    LLMBackend,
    BackendNotAvailableError,
    LLMBackendError
)
from ..utils.config import get_model_name
from .exceptions import (
    ModelNotFoundError, ModelLoadError, ModelTimeoutError,
    BackendNotAvailableError as CustomBackendNotAvailableError,
    log_and_raise_model_error
)

logger = logging.getLogger(__name__)


class AIEngine:
    """Handles AI model operations and inference using the LLM abstraction layer."""
    
    def __init__(self, 
                 backend_type: str = "auto",
                 model_path: Optional[str] = None,
                 base_url: Optional[str] = None,
                 default_model: Optional[str] = None,
                 default_embed_model: Optional[str] = None,
                 **backend_kwargs):
        """Initialize the AI engine with the specified backend.
        
        Args:
            backend_type: Backend type ("ollama", "llama-cpp", or "auto")
            model_path: Path to GGUF model file (for llama-cpp backend)
            base_url: Ollama server URL (for Ollama backend)
            default_model: Default model for text generation (if None, uses config)
            default_embed_model: Default model for embeddings (if None, uses config)
            **backend_kwargs: Additional backend-specific parameters
        """
        self.backend_type = backend_type
        self.model_path = model_path
        self.base_url = base_url
        
        # Use configured models if not explicitly provided
        self.default_model = default_model or get_model_name("chat")
        self.default_embed_model = default_embed_model or get_model_name("embeddings")
        
        self.backend_kwargs = backend_kwargs
        
        self.llm_context = None
        self.is_loaded = False
        
        # For backward compatibility
        self.model = None
        self.model_kwargs = backend_kwargs
        
    def _find_downloaded_model(self, model_type: str = "chat") -> Optional[str]:
        """Find an available model in Ollama for the specified model type.
        
        Args:
            model_type: Type of model to find (chat, legal_analysis, etc.)
            
        Returns:
            Model name if available in Ollama, or None if not found
        """
        try:
            from .ollama_client import OllamaClient
            client = OllamaClient(base_url=self.base_url)
            
            if not client.is_available():
                logger.debug("Ollama server not available")
                return None
            
            # Get the configured model name for this type
            configured_model = get_model_name(model_type)
            
            # Get list of available models in Ollama
            available_models = client.list_models()
            model_names = [model["name"] for model in available_models]
            
            # Check if the configured model is available
            if configured_model in model_names:
                logger.info(f"Found configured model for {model_type}: {configured_model}")
                return configured_model
            
            # Look for alternative models based on type
            if model_type == "legal_analysis":
                # Look for legal-specific models
                for model_name in model_names:
                    if any(keyword in model_name.lower() for keyword in ["law", "legal", "lawyer"]):
                        logger.info(f"Found legal model for {model_type}: {model_name}")
                        return model_name
            
            # Look for general models using configuration system
            # Try other configured model types as fallbacks
            fallback_types = ["chat", "query_generation", "fallback"]
            for fallback_type in fallback_types:
                if fallback_type != model_type:  # Don't try the same type again
                    try:
                        fallback_model = get_model_name(fallback_type)
                        if fallback_model in model_names:
                            logger.info(f"Found fallback model for {model_type}: {fallback_model} (from {fallback_type})")
                            return fallback_model
                    except Exception:
                        continue
            
            # Last resort: look for common model patterns in available models
            common_patterns = ["llama", "mistral", "phi", "qwen", "gemma"]
            for pattern in common_patterns:
                for model_name in model_names:
                    if pattern in model_name.lower():
                        logger.info(f"Found pattern-matched model for {model_type}: {model_name}")
                        return model_name
            
            return None
            
        except Exception as e:
            logger.debug(f"Error finding available model: {e}")
            return None

    def _determine_backend_type(self) -> str:
        """Determine the best backend type to use.
        
        Returns:
            Backend type string
        """
        if self.backend_type != "auto":
            return self.backend_type
        
        # Auto-detection logic
        available_backends = LLMFactory.get_available_backends()
        
        # Prefer Ollama if available
        if "ollama" in available_backends:
            # Check if Ollama server is running
            try:
                from .ollama_client import OllamaClient
                client = OllamaClient(base_url=self.base_url)
                if client.is_available():
                    return "ollama"
            except Exception:
                pass
        
        # Only fall back to llama-cpp if explicitly provided a model path
        if "llama-cpp" in available_backends and self.model_path:
            return "llama-cpp"
        
        # Default to Ollama even if server isn't running (user can start it)
        if "ollama" in available_backends:
            return "ollama"
        
        # Default to first available backend
        if available_backends:
            return available_backends[0]
        
        raise BackendNotAvailableError("No LLM backends available")
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """Load the model using the appropriate backend.
        
        Args:
            model_path: Path to the model file (for llama-cpp backend).
            
        Returns:
            True if model loaded successfully, False otherwise.
        """
        try:
            # Update model path if provided
            if model_path:
                self.model_path = model_path
            
            # Determine backend type
            backend_type = self._determine_backend_type()
            logger.info(f"Using backend: {backend_type}")
            
            # Create backend configuration
            if backend_type == "ollama":
                backend_config = {
                    "base_url": self.base_url,
                    "default_model": self.default_model,
                    "default_embed_model": self.default_embed_model,
                    **self.backend_kwargs
                }
            elif backend_type == "llama-cpp":
                if not self.model_path:
                    logger.error("Model path required for llama-cpp backend")
                    return False
                
                backend_config = {
                    "model_path": self.model_path,
                    "n_ctx": self.backend_kwargs.get("n_ctx", 4096),
                    "n_batch": self.backend_kwargs.get("n_batch", 512),
                    "n_threads": self.backend_kwargs.get("n_threads", None),
                    **{k: v for k, v in self.backend_kwargs.items() 
                       if k not in ["n_ctx", "n_batch", "n_threads"]}
                }
            else:
                raise ValueError(f"Unsupported backend type: {backend_type}")
            
            # Create and initialize backend
            backend = LLMFactory.create_backend(backend_type, **backend_config)
            self.llm_context = LLMContext(backend)
            
            if self.llm_context.initialize():
                self.is_loaded = True
                self.backend_type = backend_type
                
                # For backward compatibility
                self.model = self.llm_context.backend
                
                logger.info(f"AI Engine initialized successfully with {backend_type} backend")
                return True
            else:
                logger.error(f"Failed to initialize {backend_type} backend")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.is_loaded = False
            return False
    
    def _try_fallback_model(self, operation: str, model_type: str, original_error: Exception) -> Optional[str]:
        """Try to use a fallback model when the primary model fails.
        
        Args:
            operation: Description of the operation that failed
            model_type: Type of model that failed
            original_error: The original error that occurred
            
        Returns:
            Fallback model name if available, None otherwise
        """
        try:
            fallback_model = get_model_name("fallback")
            
            # Don't use the same model as fallback
            primary_model = get_model_name(model_type)
            if fallback_model == primary_model:
                logger.warning(f"Fallback model is the same as primary model for {model_type}, no fallback available")
                return None
            
            logger.warning(f"Primary {model_type} model failed for {operation}, trying fallback model: {fallback_model}")
            logger.debug(f"Original error: {original_error}")
            
            return fallback_model
            
        except Exception as e:
            logger.error(f"Failed to get fallback model: {e}")
            return None

    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 1000, 
                         temperature: float = 0.7, 
                         model: Optional[str] = None,
                         **kwargs) -> str:
        """Generate a response using the loaded model.
        
        Args:
            prompt: Input prompt for the model.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = random).
            model: Model name to use (optional, uses default if not specified).
            **kwargs: Additional generation parameters.
            
        Returns:
            Generated response text.
            
        Raises:
            RuntimeError: If model is not loaded.
            ModelNotFoundError: If the specified model is not found.
            ModelLoadError: If the model fails to load.
        """
        if not self.is_loaded or not self.llm_context:
            raise RuntimeError("Model is not loaded. Call load_model() first.")
        
        # Use default model if none specified
        if model is None:
            model = self.default_model
        
        try:
            response = self.llm_context.generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Handle streaming responses
            if hasattr(response, '__iter__') and not isinstance(response, str):
                # Streaming response - collect all chunks
                response_text = "".join(response)
            else:
                response_text = str(response)
            
            # Clean up response
            return self._clean_response(response_text)
            
        except (ModelNotFoundError, ModelLoadError, ModelTimeoutError) as e:
            # Try fallback model for model-specific errors
            fallback_model = self._try_fallback_model("text generation", "chat", e)
            if fallback_model and fallback_model != model:
                try:
                    logger.info(f"Retrying text generation with fallback model: {fallback_model}")
                    response = self.llm_context.generate(
                        prompt=prompt,
                        model=fallback_model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs
                    )
                    
                    # Handle streaming responses
                    if hasattr(response, '__iter__') and not isinstance(response, str):
                        response_text = "".join(response)
                    else:
                        response_text = str(response)
                    
                    return self._clean_response(response_text)
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback model also failed: {fallback_error}")
                    # Raise the original error, not the fallback error
                    log_and_raise_model_error(e, logger)
            else:
                log_and_raise_model_error(e, logger)
                
        except (BackendNotAvailableError, LLMBackendError) as e:
            logger.error(f"Error generating response: {e}")
            raise RuntimeError(f"Generation failed: {e}") from e
    
    def generate_chat_response(self, 
                              messages: List[Dict[str, str]], 
                              max_tokens: int = 1000, 
                              temperature: float = 0.7,
                              model: Optional[str] = None,
                              **kwargs) -> str:
        """Generate a chat response using the loaded model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            model: Model name to use (optional, uses default if not specified).
            **kwargs: Additional generation parameters.
            
        Returns:
            Generated response text.
        """
        if not self.is_loaded or not self.llm_context:
            raise RuntimeError("Model is not loaded. Call load_model() first.")
        
        try:
            response = self.llm_context.chat(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Handle streaming responses
            if hasattr(response, '__iter__') and not isinstance(response, str):
                # Streaming response - collect all chunks
                response_text = "".join(response)
            else:
                response_text = str(response)
            
            return self._clean_response(response_text)
            
        except (BackendNotAvailableError, LLMBackendError) as e:
            logger.error(f"Error generating chat response: {e}")
            raise RuntimeError(f"Chat generation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error generating chat response: {e}")
            raise
    
    def generate_embeddings(self, 
                           text: Union[str, List[str]], 
                           model: Optional[str] = None) -> Union[List[float], List[List[float]]]:
        """Generate embeddings for the input text.
        
        Args:
            text: Text or list of texts to embed.
            model: Embedding model name (optional, uses default if not specified).
            
        Returns:
            Embedding vector(s).
        """
        if not self.is_loaded or not self.llm_context:
            raise RuntimeError("Model is not loaded. Call load_model() first.")
        
        try:
            return self.llm_context.embed(input_text=text, model=model)
        except (BackendNotAvailableError, LLMBackendError) as e:
            logger.error(f"Error generating embeddings: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error generating embeddings: {e}")
            raise
    
    def analyze_document(self, text: str, analysis_type: str = "summary") -> str:
        """Analyze a document using the AI model.
        
        Args:
            text: Document text to analyze.
            analysis_type: Type of analysis ("summary", "key_points", "legal_issues").
            
        Returns:
            Analysis result.
            
        Raises:
            ModelNotFoundError: If the legal analysis model is not found.
            ModelLoadError: If the model fails to load.
        """
        if analysis_type == "summary":
            prompt = self._create_summary_prompt(text)
        elif analysis_type == "key_points":
            prompt = self._create_key_points_prompt(text)
        elif analysis_type == "legal_issues":
            prompt = self._create_legal_issues_prompt(text)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        # Use legal_analysis model for document analysis
        legal_model = get_model_name("legal_analysis")
        
        # Convert to chat format for better model performance
        messages = [
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        try:
            return self.generate_chat_response(messages, model=legal_model, max_tokens=1500, temperature=0.3)
        except (ModelNotFoundError, ModelLoadError, ModelTimeoutError) as e:
            # Try fallback for legal analysis
            fallback_model = self._try_fallback_model("document analysis", "legal_analysis", e)
            if fallback_model and fallback_model != legal_model:
                logger.info(f"Retrying document analysis with fallback model: {fallback_model}")
                return self.generate_chat_response(messages, model=fallback_model, max_tokens=1500, temperature=0.3)
            else:
                log_and_raise_model_error(e, logger)
        
    def generate_search_query(self, text: str, database: str = "westlaw") -> str:
        """Generate a search query for legal databases.
        
        Args:
            text: Document text to base the query on.
            database: Target database ("westlaw", "lexisnexis", "casetext").
            
        Returns:
            Generated search query.
            
        Raises:
            ModelNotFoundError: If the query generation model is not found.
            ModelLoadError: If the model fails to load.
        """
        prompt = self._create_search_query_prompt(text, database)
        
        # DEBUG: Log the actual prompt being sent
        logger.info(f"=== SEARCH QUERY GENERATION DEBUG ===")
        logger.info(f"Database: {database}")
        logger.info(f"Text length: {len(text)} characters")
        logger.info(f"Prompt being sent:\n{prompt}")
        logger.info(f"=== END DEBUG ===")
        
        # Use query_generation model for search query generation
        query_model = get_model_name("query_generation")
        logger.info(f"Using query model: {query_model}")
        
        # TEMPORARY: Try raw generation instead of chat format
        try:
            response = self.generate_response(prompt, model=query_model, max_tokens=200, temperature=0.2)
            logger.info(f"Raw AI response: {repr(response)}")
            return response
        except (ModelNotFoundError, ModelLoadError, ModelTimeoutError) as e:
            # Try fallback for query generation
            fallback_model = self._try_fallback_model("search query generation", "query_generation", e)
            if fallback_model and fallback_model != query_model:
                logger.info(f"Retrying search query generation with fallback model: {fallback_model}")
                response = self.generate_response(prompt, model=fallback_model, max_tokens=200, temperature=0.2)
                logger.info(f"Raw AI fallback response: {repr(response)}")
                return response
            else:
                log_and_raise_model_error(e, logger)
    
    def list_models(self) -> List[str]:
        """List available models.
        
        Returns:
            List of model names.
        """
        if not self.is_loaded or not self.llm_context:
            return []
        
        try:
            return self.llm_context.list_models()
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def switch_backend(self, 
                      backend_type: str, 
                      **backend_config) -> bool:
        """Switch to a different backend.
        
        Args:
            backend_type: New backend type ("ollama" or "llama-cpp").
            **backend_config: Configuration for the new backend.
            
        Returns:
            True if switch successful, False otherwise.
        """
        try:
            new_backend = LLMFactory.create_backend(backend_type, **backend_config)
            
            if self.llm_context:
                success = self.llm_context.switch_backend(new_backend)
                if success:
                    self.backend_type = backend_type
                    logger.info(f"Successfully switched to {backend_type} backend")
                return success
            else:
                self.llm_context = LLMContext(new_backend)
                success = self.llm_context.initialize()
                if success:
                    self.backend_type = backend_type
                    self.is_loaded = True
                    logger.info(f"Successfully initialized {backend_type} backend")
                return success
                
        except Exception as e:
            logger.error(f"Failed to switch backend: {e}")
            return False
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the current backend.
        
        Returns:
            Dictionary with backend information.
        """
        if not self.llm_context:
            return {"backend_type": "none", "is_loaded": False}
        
        return self.llm_context.get_backend_info()
    
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
            return f"""You are a legal research expert. Your task is to create a Westlaw database search query using Terms and Connectors syntax based on the document excerpt provided below.

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

EXCELLENT WESTLAW EXAMPLES:
- negligen! /p "motor vehicle" /s injur! & damag!
- (contract | agreement) /s breach /p (remedy | damag! | restitution)
- "personal injury" /p automobile /s insurance /3 (claim! | coverage)
- liabil! /s (product! | manufactur!) & defect! /p injur!
- "medical malpractice" /p (hospital | physician | doctor) /s "standard of care"
- employment /3 discriminat! /p (title | "civil rights") & damag!
- (tort! | negligen!) /s "proximate cause" /p foresee!
- "breach of contract" /s (anticipat! | expect!) /p damag!

AVOID including:
- Specific dates, times, or years unless legally relevant
- Personal names of individuals (except in case citations)
- Specific hospital names, company names, or addresses
- Medical record numbers, case numbers, or file references
- Irrelevant procedural details
- Focus on LEGAL CONCEPTS and CAUSES OF ACTION

IMPORTANT: Output only the Westlaw database search query - no explanations, no additional text.

Document excerpt:
{text[:2000]}"""
        
        elif database == "lexisnexis" or database == "lexis":
            return f"""You are a legal research expert. Your task is to create a LexisNexis database search query using boolean operators based on the document excerpt provided below.

LEXISNEXIS SYNTAX RULES:
- Use AND for required terms
- Use OR for alternative terms
- Use NOT to exclude terms
- Use W/n for within n words (e.g., W/3 for within 3 words)
- Use PRE/n for term A preceding term B within n words
- Use quotes for exact phrases: "personal injury"
- Use parentheses for grouping: (contract OR agreement) AND breach

EXCELLENT LEXISNEXIS EXAMPLES:
- negligence AND "motor vehicle" AND injury AND damages
- (contract OR agreement) AND breach AND (remedy OR damages OR restitution)
- "personal injury" AND automobile AND insurance AND (claim OR coverage)
- liability AND (product OR manufacturer) AND defect AND injury
- "medical malpractice" AND (hospital OR physician) AND "standard of care"
- employment AND discrimination AND ("title vii" OR "civil rights") AND damages
- (tort OR negligence) AND "proximate cause" AND foreseeability
- "breach of contract" AND (anticipatory OR expectation) AND damages

AVOID including:
- Specific dates, times, or years unless legally relevant
- Personal names of individuals (except in case citations)
- Specific hospital names, company names, or addresses
- Medical record numbers, case numbers, or file references
- Irrelevant procedural details
- Focus on LEGAL CONCEPTS and CAUSES OF ACTION

IMPORTANT: Output only the LexisNexis database search query - no explanations, no additional text.

Document excerpt:
{text[:2000]}"""
        
        elif database == "bloomberg":
            return f"""You are a legal research expert. Your task is to create a Bloomberg Law database search query using their advanced syntax based on the document excerpt provided below.

BLOOMBERG LAW SYNTAX RULES:
- Use AND for required terms
- Use OR for alternative terms
- Use NOT to exclude terms
- Use NEAR/n for proximity (e.g., NEAR/5 for within 5 words)
- Use quotes for exact phrases: "personal injury"
- Use parentheses for grouping: (contract OR agreement) AND breach
- Use field searches: title:(contract breach) or headnotes:(negligence)

EXCELLENT BLOOMBERG LAW EXAMPLES:
- negligence AND "motor vehicle" AND injury AND damages
- (contract OR agreement) AND breach AND (remedy OR damages)
- "personal injury" AND automobile AND insurance NEAR/3 claim
- liability AND (product OR manufacturer) AND defect AND injury
- "medical malpractice" AND physician AND "standard of care"
- employment AND discrimination AND "title vii" AND damages
- tort AND "proximate cause" AND foreseeability
- "breach of contract" AND expectation AND damages
- headnotes:(negligence AND "duty of care" AND breach)

AVOID including:
- Specific dates, times, or years unless legally relevant
- Personal names of individuals (except in case citations)
- Specific hospital names, company names, or addresses
- Medical record numbers, case numbers, or file references
- Irrelevant procedural details
- Focus on LEGAL CONCEPTS and CAUSES OF ACTION

IMPORTANT: Output only the Bloomberg Law database search query - no explanations, no additional text.

Document excerpt:
{text[:2000]}"""
        
        else:  # casetext, fastcase, or other
            return f"""You are a legal research expert. Your task is to create a database search query for {database} using natural language and boolean operators based on the document excerpt provided below.

GENERAL LEGAL DATABASE SYNTAX:
- Use AND for required terms
- Use OR for alternative terms
- Use NOT to exclude terms
- Use quotes for exact phrases: "personal injury"
- Use parentheses for grouping: (contract OR agreement) AND breach

EXCELLENT EXAMPLES:
- negligence AND "motor vehicle" AND injury AND damages
- (contract OR agreement) AND breach AND remedy
- "personal injury" AND automobile AND insurance
- liability AND product AND defect AND injury
- "medical malpractice" AND physician AND "standard of care"
- employment AND discrimination AND damages
- tort AND "proximate cause"
- "breach of contract" AND damages

AVOID including:
- Specific dates, times, or years unless legally relevant
- Personal names of individuals (except in case citations)
- Specific hospital names, company names, or addresses
- Medical record numbers, case numbers, or file references
- Irrelevant procedural details
- Focus on LEGAL CONCEPTS and CAUSES OF ACTION

IMPORTANT: Output only the {database} database search query - no explanations, no additional text.

Document excerpt:
{text[:2000]}"""

    def _clean_response(self, text: str) -> str:
        """Clean and format the response text."""
        if not text:
            return ""
        
        # TEMPORARILY DISABLED FOR TESTING - return raw response
        return text.strip()
        
        # # Remove common chat format artifacts
        # text = text.replace("[/INST]", "").replace("[INST]", "")
        # text = text.replace("<s>", "").replace("</s>", "")
        # text = text.replace("[/type]", "")  # Remove [/type] artifacts
        # text = text.replace("[/]", "")  # Remove [/] artifacts
        
        # # Remove prompt echoes more comprehensively
        # text = re.sub(r'^.*?based on the document excerpt.*?database search query.*?\.\s*', '', text, flags=re.IGNORECASE | re.DOTALL)
        # text = re.sub(r'^.*?create a.*?database.*?query.*?\.\s*', '', text, flags=re.IGNORECASE | re.DOTALL)
        # text = re.sub(r'^.*?output only the.*?database.*?query.*?\.\s*', '', text, flags=re.IGNORECASE | re.DOTALL)
        # text = re.sub(r'^Please provide the.*?search query.*?\.\s*', '', text, flags=re.IGNORECASE)
        # text = re.sub(r'^Based on this document.*?\?\s*', '', text, flags=re.IGNORECASE)
        
        # # Clean leading/trailing whitespace and quotes
        # text = text.strip()
        
        # # If the response is wrapped in quotes, clean them up
        # if text.startswith('"') and text.endswith('"'):
        #     text = text[1:-1].strip()
        
        # return text

    def unload_model(self) -> None:
        """Unload the model to free memory."""
        if self.llm_context:
            try:
                self.llm_context.unload_model()
            except Exception as e:
                logger.warning(f"Error unloading model: {e}")
            
            self.llm_context = None
        
        self.is_loaded = False
        self.model = None  # For backward compatibility
        logger.info("Model unloaded")
            
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.unload_model()


# Backward compatibility functions
def create_ai_engine_from_config(config: Dict[str, Any]) -> AIEngine:
    """Create an AI engine from configuration dictionary.
    
    Args:
        config: Configuration dictionary with backend settings
        
    Returns:
        Configured AIEngine instance
    """
    # Check for new LLM configuration structure
    llm_config = config.get("llm", {})
    backend_type = llm_config.get("backend", "auto")
    
    # Extract backend-specific configuration
    backend_config = {}
    
    if backend_type == "ollama" or (backend_type == "auto" and "ollama" in llm_config):
        ollama_config = llm_config.get("ollama", {})
        backend_config.update({
            "base_url": ollama_config.get("base_url"),
            "default_model": ollama_config.get("default_model", get_model_name("chat")),
            "default_embed_model": ollama_config.get("default_embed_model", get_model_name("embeddings")),
            "timeout": ollama_config.get("timeout", 30),
            "max_retries": ollama_config.get("max_retries", 3),
            "retry_delay": ollama_config.get("retry_delay", 1.0)
        })
    
    if backend_type == "llama-cpp" or (backend_type == "auto" and "llama_cpp" in llm_config):
        llama_config = llm_config.get("llama_cpp", {})
        backend_config.update({
            "model_path": llama_config.get("model_path"),
            "n_ctx": llama_config.get("n_ctx", 4096),
            "n_batch": llama_config.get("n_batch", 512),
            "n_threads": llama_config.get("n_threads"),
            "temperature": llama_config.get("temperature", 0.7),
            "max_tokens": llama_config.get("max_tokens", 1000)
        })
    
    # Fallback to legacy configuration if no LLM config found
    if not llm_config and "model" in config:
        logger.info("Using legacy model configuration")
        legacy_model = config["model"]
        backend_type = "llama-cpp"  # Legacy always used direct model paths
        backend_config.update({
            "model_path": legacy_model.get("path"),
            "n_ctx": legacy_model.get("context_length", 4096),
            "n_batch": 512,  # Default value
            "n_threads": legacy_model.get("threads"),
            "temperature": legacy_model.get("temperature", 0.7),
            "max_tokens": legacy_model.get("max_tokens", 1000)
        })
    
    return AIEngine(backend_type=backend_type, **backend_config) 