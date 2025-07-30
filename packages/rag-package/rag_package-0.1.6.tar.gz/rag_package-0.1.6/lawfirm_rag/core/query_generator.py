"""
Query Generator module for LawFirm-RAG.

Handles generation of optimized search queries for legal databases.
"""

import logging
from typing import Dict, Any, Optional, List
from .ai_engine import AIEngine

logger = logging.getLogger(__name__)


class QueryGenerator:
    """Generates optimized search queries for legal databases."""
    
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        """Initialize the query generator.
        
        Args:
            ai_engine: AI engine instance for query generation.
        """
        self.ai_engine = ai_engine
        self.database_templates = {
            "westlaw": {
                "name": "Westlaw",
                "syntax": "Terms and Connectors",
                "operators": ["&", "|", "/s", "/p", "/3", "/5", "!", "%"],
                "description": "Use & for AND, | for OR, /s for same sentence, /p for same paragraph, ! for truncation"
            },
            "lexisnexis": {
                "name": "LexisNexis",
                "syntax": "Boolean",
                "operators": ["AND", "OR", "NOT", "W/n", "PRE/n"],
                "description": "Use AND, OR, NOT operators, W/n for within n words, PRE/n for precedence"
            },
            "lexis": {
                "name": "LexisNexis",
                "syntax": "Boolean", 
                "operators": ["AND", "OR", "NOT", "W/n", "PRE/n"],
                "description": "Use AND, OR, NOT operators, W/n for within n words, PRE/n for precedence"
            },
            "bloomberg": {
                "name": "Bloomberg Law",
                "syntax": "Boolean + Field Search",
                "operators": ["AND", "OR", "NOT", "NEAR/n", "title:", "headnotes:"],
                "description": "Use AND, OR, NOT operators, NEAR/n for proximity, field searches with title: and headnotes:"
            },
            "casetext": {
                "name": "Casetext",
                "syntax": "Natural Language + Boolean",
                "operators": ["AND", "OR", "NOT", "NEAR"],
                "description": "Supports natural language queries and boolean operators"
            },
            "fastcase": {
                "name": "Fastcase",
                "syntax": "Boolean",
                "operators": ["AND", "OR", "NOT", "&", "|"],
                "description": "Use AND, OR, NOT operators or & and | symbols"
            }
        }
        
    def generate_query(self, text: str, database: str = "westlaw", 
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a search query for a specific legal database.
        
        Args:
            text: Document text to base the query on.
            database: Target database ("westlaw", "lexisnexis", "casetext").
            context: Additional context for query generation.
            
        Returns:
            Dictionary containing the generated query and metadata.
        """
        if database not in self.database_templates:
            raise ValueError(f"Unsupported database: {database}")
            
        db_info = self.database_templates[database]
        
        try:
            # Use AI engine if available
            if self.ai_engine and self.ai_engine.is_loaded:
                query = self.ai_engine.generate_search_query(text, database)
            else:
                # Fallback to rule-based query generation
                query = self._generate_fallback_query(text, database)
                
            return {
                "query": query.strip(),
                "database": database,
                "database_info": db_info,
                "confidence": self._estimate_confidence(query, text),
                "suggestions": self._generate_suggestions(query, database),
                "metadata": {
                    "text_length": len(text),
                    "method": "ai" if self.ai_engine and self.ai_engine.is_loaded else "fallback"
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating query for {database}: {e}")
            raise
            
    def generate_multiple_queries(self, text: str, 
                                databases: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """Generate queries for multiple databases.
        
        Args:
            text: Document text to base queries on.
            databases: List of databases to generate queries for. If None, uses all supported.
            
        Returns:
            Dictionary mapping database names to query results.
        """
        if databases is None:
            databases = list(self.database_templates.keys())
            
        results = {}
        for db in databases:
            try:
                results[db] = self.generate_query(text, db)
            except Exception as e:
                logger.error(f"Failed to generate query for {db}: {e}")
                results[db] = {
                    "error": str(e),
                    "database": db
                }
                
        return results
        
    def _generate_fallback_query(self, text: str, database: str) -> str:
        """Generate a basic query using rule-based methods when AI is not available.
        
        Args:
            text: Document text.
            database: Target database.
            
        Returns:
            Generated query string.
        """
        # Extract key terms (simplified approach)
        words = text.lower().split()
        
        # Common legal terms that are often important
        legal_terms = [
            "contract", "agreement", "liability", "negligence", "breach", 
            "damages", "plaintiff", "defendant", "court", "statute",
            "regulation", "compliance", "violation", "penalty", "rights",
            "obligation", "duty", "standard", "reasonable", "material"
        ]
        
        # Find legal terms in the text
        found_terms = [term for term in legal_terms if term in words]
        
        # Extract potential case names (simplified - look for "v." pattern)
        case_patterns = []
        for i, word in enumerate(words):
            if word == "v." and i > 0 and i < len(words) - 1:
                case_patterns.append(f"{words[i-1]} v. {words[i+1]}")
                
        # Build query based on database syntax
        if database == "westlaw":
            if found_terms:
                query_parts = found_terms[:3]  # Limit to top 3 terms
                query = " & ".join(query_parts)
            else:
                # Extract first few meaningful words
                meaningful_words = [w for w in words[:10] if len(w) > 3][:3]
                query = " & ".join(meaningful_words)
                
        elif database == "lexisnexis":
            if found_terms:
                query_parts = found_terms[:3]
                query = " AND ".join(query_parts)
            else:
                meaningful_words = [w for w in words[:10] if len(w) > 3][:3]
                query = " AND ".join(meaningful_words)
                
        elif database == "casetext":
            if found_terms:
                query = " ".join(found_terms[:5])  # More natural language
            else:
                query = " ".join(words[:10])  # First 10 words
                
        else:
            query = " ".join(words[:5])  # Generic fallback
            
        return query
        
    def _estimate_confidence(self, query: str, text: str) -> float:
        """Estimate confidence in the generated query.
        
        Args:
            query: Generated query.
            text: Original text.
            
        Returns:
            Confidence score between 0.0 and 1.0.
        """
        # Start with lower base confidence
        confidence = 0.3  # More conservative base
        
        # Check for proper syntax usage
        query_lower = query.lower()
        
        # For Westlaw queries, check for proper operators
        westlaw_operators = ["&", "|", "/s", "/p", "/3", "/5", "!", "%", "(", ")"]
        operator_count = sum(1 for op in westlaw_operators if op in query)
        if operator_count >= 2:
            confidence += 0.25  # Good complex Westlaw syntax
        elif operator_count >= 1:
            confidence += 0.15  # Basic Westlaw syntax
        
        # Check for legal terms
        legal_terms = ["contract", "liability", "negligence", "statute", "court", 
                      "damages", "breach", "injury", "insurance", "claim"]
        legal_term_count = sum(1 for term in legal_terms if term in query_lower)
        confidence += min(legal_term_count * 0.05, 0.2)  # More conservative
        
        # Check query length (optimal range)
        query_words = len(query.split())
        if 3 <= query_words <= 8:
            confidence += 0.15
        elif query_words < 2:
            confidence -= 0.3  # Penalize very short queries more
        elif query_words > 15:
            confidence -= 0.2  # Penalize very long queries
            
        # Bonus for AI engine, but more modest
        if self.ai_engine and self.ai_engine.is_loaded:
            confidence += 0.15
        else:
            confidence -= 0.1  # Fallback queries are less reliable
            
        # Check for quoted phrases (good practice)
        if '"' in query:
            confidence += 0.1
            
        return min(max(confidence, 0.1), 0.9)  # Cap at 90% max confidence
        
    def _generate_suggestions(self, query: str, database: str) -> List[str]:
        """Generate suggestions for improving the query.
        
        Args:
            query: Generated query.
            database: Target database.
            
        Returns:
            List of suggestion strings.
        """
        suggestions = []
        db_info = self.database_templates[database]
        
        # Check query length
        query_words = len(query.split())
        if query_words < 3:
            suggestions.append("Consider adding more specific legal terms to narrow your search")
        elif query_words > 20:
            suggestions.append("Consider simplifying the query for better performance")
            
        # Database-specific suggestions
        if database == "westlaw":
            if "&" not in query and "|" not in query:
                suggestions.append("Consider using & (AND) or | (OR) operators for better precision")
            if "/s" not in query and "/p" not in query and "/3" not in query:
                suggestions.append("Use proximity operators: /s (same sentence), /p (same paragraph), /3 (within 3 words)")
            if "!" not in query:
                suggestions.append("Use ! for truncation to find word variations (e.g., negligen! for negligent/negligence)")
            suggestions.append("Group related terms with parentheses: (contract | agreement) & breach")
            suggestions.append("Focus on legal concepts rather than specific names or dates")
            
        elif database in ["lexisnexis", "lexis"]:
            if "AND" not in query and "OR" not in query:
                suggestions.append("Consider using AND or OR operators for better control")
            suggestions.append("Use W/3 or W/5 for proximity searching within n words")
            suggestions.append("Use PRE/3 when word order matters (A before B within 3 words)")
            suggestions.append("Focus on legal causes of action and remedies")
            
        elif database == "bloomberg":
            if "AND" not in query and "OR" not in query:
                suggestions.append("Consider using AND or OR operators for better control")
            suggestions.append("Use NEAR/5 for proximity searching within 5 words")
            suggestions.append("Try field searches: title:(your terms) or headnotes:(legal concepts)")
            suggestions.append("Focus on substantive legal issues rather than procedural details")
            
        elif database == "casetext":
            suggestions.append("Try natural language queries for broader results")
            suggestions.append("Use boolean operators (AND, OR) for more precise searches")
            suggestions.append("Focus on legal principles and case outcomes")
            
        elif database == "fastcase":
            suggestions.append("Use AND, OR, NOT operators or & and | symbols")
            suggestions.append("Focus on legal issues and statutory citations")
            
        # General suggestions for all databases
        suggestions.append("Avoid including specific dates, names, or locations unless legally relevant")
        suggestions.append("Focus on causes of action, legal standards, and remedies")
        suggestions.append(f"Syntax help: {db_info['description']}")
        
        return suggestions
        
    def get_database_info(self, database: str) -> Dict[str, Any]:
        """Get information about a specific database.
        
        Args:
            database: Database name.
            
        Returns:
            Database information dictionary.
        """
        if database not in self.database_templates:
            raise ValueError(f"Unknown database: {database}")
            
        return self.database_templates[database].copy()
        
    def list_supported_databases(self) -> List[str]:
        """Get list of supported databases.
        
        Returns:
            List of supported database names.
        """
        return list(self.database_templates.keys()) 