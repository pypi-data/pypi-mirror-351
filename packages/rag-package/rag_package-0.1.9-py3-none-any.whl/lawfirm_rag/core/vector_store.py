"""
ChromaDB Vector Store Implementation

This module provides a user-friendly interface to ChromaDB with:
- Simple API for common operations (add, search, delete)
- Automatic embedding generation and management
- Collection management with sensible defaults
- Batch operations for large-scale document processing
- Advanced filtering and search capabilities
"""

import os
import logging
from typing import List, Dict, Optional, Union, Any, Tuple
from pathlib import Path
import uuid
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Install with: pip install chromadb")

from .embeddings import LocalEmbeddingGenerator, create_embedding_generator

logger = logging.getLogger(__name__)


class ChromaEmbeddingFunction:
    """Custom embedding function that uses our LocalEmbeddingGenerator."""
    
    def __init__(self, embedding_generator: LocalEmbeddingGenerator):
        self.embedding_generator = embedding_generator
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = self.embedding_generator.embed_batch(input, show_progress=False)
        return [embedding.tolist() for embedding in embeddings]


class VectorStoreConfig:
    """Configuration for different vector store setups."""
    
    COLLECTION_CONFIGS = {
        "legal": {
            "description": "Legal documents and case law",
            "metadata_fields": ["document_type", "jurisdiction", "practice_area", "date_created", "source"],
            "default_metadata": {"document_type": "legal", "practice_area": "general"},
            "search_fields": ["practice_area", "jurisdiction", "document_type"],
            "chunk_size": 1000,
            "chunk_overlap": 200
        },
        "business": {
            "description": "Business documents and policies",
            "metadata_fields": ["document_type", "department", "category", "date_created", "source"],
            "default_metadata": {"document_type": "business", "category": "general"},
            "search_fields": ["department", "category", "document_type"],
            "chunk_size": 800,
            "chunk_overlap": 150
        },
        "academic": {
            "description": "Academic papers and research",
            "metadata_fields": ["document_type", "subject", "author", "publication_date", "source"],
            "default_metadata": {"document_type": "academic", "subject": "general"},
            "search_fields": ["subject", "author", "document_type"],
            "chunk_size": 1200,
            "chunk_overlap": 250
        },
        "general": {
            "description": "General purpose document collection",
            "metadata_fields": ["document_type", "category", "tags", "date_created", "source"],
            "default_metadata": {"document_type": "general", "category": "uncategorized"},
            "search_fields": ["category", "tags", "document_type"],
            "chunk_size": 1000,
            "chunk_overlap": 200
        }
    }
    
    @classmethod
    def get_config(cls, collection_type: str) -> Dict:
        """Get configuration for a specific collection type."""
        return cls.COLLECTION_CONFIGS.get(collection_type, cls.COLLECTION_CONFIGS["general"])


class DocumentVectorStore:
    """
    High-level interface for ChromaDB vector operations.
    
    Designed for maximum ease of use while supporting advanced features.
    """
    
    def __init__(
        self,
        collection_name: str = "documents",
        collection_type: str = "general",
        data_dir: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L12-v2",
        embedding_generator: Optional[LocalEmbeddingGenerator] = None,
        **chroma_settings
    ):
        """
        Initialize the vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
            collection_type: Type of collection (legal, business, academic, general)
            data_dir: Directory to store ChromaDB data
            embedding_model: Embedding model to use
            embedding_generator: Pre-configured embedding generator
            **chroma_settings: Additional ChromaDB settings
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is required for vector store operations. "
                "Install with: pip install chromadb"
            )
        
        self.collection_name = collection_name
        self.collection_type = collection_type
        self.config = VectorStoreConfig.get_config(collection_type)
        
        # Set up data directory
        if data_dir is None:
            data_dir = os.path.expanduser("~/.lawfirm-rag/vector_store")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding generator
        if embedding_generator is None:
            self.embedding_generator = create_embedding_generator(
                model_name=embedding_model,
                use_case=collection_type
            )
        else:
            self.embedding_generator = embedding_generator
        
        # Initialize ChromaDB client
        settings = Settings(
            persist_directory=str(self.data_dir),
            anonymized_telemetry=False,
            **chroma_settings
        )
        
        self.client = chromadb.PersistentClient(settings=settings)
        self.embedding_function = ChromaEmbeddingFunction(self.embedding_generator)
        
        # Get or create collection
        self._collection = None
        self._initialize_collection()
        
        logger.info(f"Initialized DocumentVectorStore: {collection_name} ({collection_type})")
    
    def _initialize_collection(self):
        """Initialize the ChromaDB collection."""
        try:
            # Try to get existing collection
            self._collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except ValueError:
            # Create new collection
            self._collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"type": self.collection_type, "description": self.config["description"]}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    @property
    def collection(self):
        """Get the ChromaDB collection."""
        return self._collection
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100,
        progress_callback: Optional[callable] = None
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of document texts to add
            metadatas: Optional metadata for each document
            ids: Optional custom IDs for documents
            batch_size: Batch size for processing
            progress_callback: Optional callback function(processed, total, batch_num)
            
        Returns:
            List of document IDs that were added
        """
        if not texts:
            return []
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Prepare metadata
        if metadatas is None:
            metadatas = [self.config["default_metadata"].copy() for _ in texts]
        else:
            # Ensure all metadata has required fields
            for i, metadata in enumerate(metadatas):
                enriched_metadata = self.config["default_metadata"].copy()
                enriched_metadata.update(metadata)
                # Add timestamp if not present
                if "date_created" not in enriched_metadata:
                    enriched_metadata["date_created"] = datetime.now().isoformat()
                metadatas[i] = enriched_metadata
        
        # Validate input lengths
        if not (len(texts) == len(metadatas) == len(ids)):
            raise ValueError("texts, metadatas, and ids must have the same length")
        
        # Process in batches for large datasets
        added_ids = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))
            batch_texts = texts[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_ids = ids[i:batch_end]
            batch_num = i // batch_size + 1
            
            try:
                self.collection.add(
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                added_ids.extend(batch_ids)
                logger.info(f"Added batch {batch_num}/{total_batches}: {len(batch_texts)} documents")
                
                # Call progress callback if provided
                if progress_callback:
                    try:
                        progress_callback(len(added_ids), len(texts), batch_num)
                    except Exception as e:
                        logger.warning(f"Progress callback failed: {e}")
                
            except Exception as e:
                logger.error(f"Failed to add batch {batch_num}: {e}")
                # Continue with next batch
                continue
        
        logger.info(f"Successfully added {len(added_ids)} documents to {self.collection_name}")
        return added_ids
    
    def add_document(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a single document to the vector store.
        
        Args:
            text: Document text
            metadata: Optional metadata
            doc_id: Optional custom ID
            
        Returns:
            Document ID that was added
        """
        ids = self.add_documents([text], [metadata] if metadata else None, [doc_id] if doc_id else None)
        return ids[0] if ids else None
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict] = None,
        include_distances: bool = True
    ) -> Dict:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            include_distances: Whether to include similarity distances
            
        Returns:
            Dictionary containing results with documents, metadata, and optionally distances
        """
        try:
            # Prepare include list
            include = ["documents", "metadatas"]
            if include_distances:
                include.append("distances")
            
            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata,
                include=include
            )
            
            # Format results for easier use
            formatted_results = {
                "query": query,
                "total_results": len(results["documents"][0]) if results["documents"] else 0,
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "ids": results["ids"][0] if results["ids"] else []
            }
            
            if include_distances and "distances" in results:
                formatted_results["distances"] = results["distances"][0]
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"query": query, "total_results": 0, "documents": [], "metadatas": [], "ids": []}
    
    def batch_search(
        self,
        queries: List[str],
        n_results: int = 10,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Perform multiple searches efficiently.
        
        Args:
            queries: List of search queries
            n_results: Number of results per query
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results for each query
        """
        try:
            results = self.collection.query(
                query_texts=queries,
                n_results=n_results,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i, query in enumerate(queries):
                formatted_results.append({
                    "query": query,
                    "total_results": len(results["documents"][i]) if results["documents"] else 0,
                    "documents": results["documents"][i] if results["documents"] else [],
                    "metadatas": results["metadatas"][i] if results["metadatas"] else [],
                    "ids": results["ids"][i] if results["ids"] else [],
                    "distances": results["distances"][i] if results.get("distances") else []
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Batch search failed: {e}")
            return [{"query": q, "total_results": 0, "documents": [], "metadatas": [], "ids": []} for q in queries]
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Get a specific document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            result = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if result["documents"] and result["documents"][0]:
                return {
                    "id": doc_id,
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0] if result["metadatas"] else {}
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a single document.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        return self.delete_documents([doc_id])
    
    def update_document(
        self,
        doc_id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update a document's text or metadata.
        
        Args:
            doc_id: Document ID
            text: New text (if provided)
            metadata: New metadata (if provided)
            
        Returns:
            True if successful
        """
        try:
            update_data = {"ids": [doc_id]}
            
            if text is not None:
                update_data["documents"] = [text]
            
            if metadata is not None:
                # Merge with existing metadata
                existing = self.get_document(doc_id)
                if existing:
                    existing_metadata = existing.get("metadata", {})
                    existing_metadata.update(metadata)
                    update_data["metadatas"] = [existing_metadata]
                else:
                    update_data["metadatas"] = [metadata]
            
            self.collection.update(**update_data)
            logger.info(f"Updated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            collection_metadata = self.collection.metadata or {}
            
            return {
                "collection_name": self.collection_name,
                "collection_type": self.collection_type,
                "total_documents": count,
                "embedding_model": self.embedding_generator.model_name,
                "embedding_dimensions": self.embedding_generator.dimensions,
                "data_directory": str(self.data_dir),
                "collection_metadata": collection_metadata,
                "config": self.config
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            # Get all document IDs
            all_docs = self.collection.get(include=[])
            if all_docs["ids"]:
                self.collection.delete(ids=all_docs["ids"])
            logger.info(f"Cleared collection {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # ChromaDB handles persistence automatically
        pass


def create_vector_store(
    collection_name: str = "documents",
    collection_type: str = "general",
    **kwargs
) -> DocumentVectorStore:
    """
    Create a vector store with sensible defaults.
    
    Args:
        collection_name: Name of the collection
        collection_type: Type of collection (legal, business, academic, general)
        **kwargs: Additional arguments for DocumentVectorStore
        
    Returns:
        Configured DocumentVectorStore instance
    """
    return DocumentVectorStore(
        collection_name=collection_name,
        collection_type=collection_type,
        **kwargs
    )


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create a legal document vector store
    with create_vector_store("legal_docs", "legal") as store:
        # Add some sample documents
        texts = [
            "This contract establishes the terms and conditions for the sale of goods.",
            "The defendant is liable for damages caused by negligent driving.",
            "Intellectual property rights include patents, trademarks, and copyrights."
        ]
        
        metadatas = [
            {"practice_area": "contracts", "document_type": "agreement"},
            {"practice_area": "tort_law", "document_type": "case_law"},
            {"practice_area": "ip_law", "document_type": "statute"}
        ]
        
        # Add documents
        ids = store.add_documents(texts, metadatas)
        print(f"Added documents with IDs: {ids}")
        
        # Search
        results = store.search("contract law", n_results=5)
        print(f"Search results: {results['total_results']} found")
        
        # Get stats
        stats = store.get_collection_stats()
        print(f"Collection stats: {stats}") 