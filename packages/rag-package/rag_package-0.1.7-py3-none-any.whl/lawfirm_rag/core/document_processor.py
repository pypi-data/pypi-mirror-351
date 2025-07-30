"""
Document processing module for LawFirm-RAG.

Handles document upload, text extraction, and document management.
"""

import tempfile
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

try:
    import PyPDF2
    import docx
except ImportError:
    PyPDF2 = None
    docx = None

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document processing and text extraction."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize the document processor.
        
        Args:
            temp_dir: Directory for temporary file storage. If None, uses system temp.
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
    def create_session(self) -> str:
        """Create a new document processing session.
        
        Returns:
            Session ID string.
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "documents": [],
            "extracted_texts": {},
            "created_at": None
        }
        return session_id
        
    def extract_text(self, file_path: Path) -> str:
        """Extract text from a document file.
        
        Args:
            file_path: Path to the document file.
            
        Returns:
            Extracted text content.
            
        Raises:
            ValueError: If file format is not supported.
            ImportError: If required libraries are not installed.
        """
        ext = file_path.suffix.lower()
        text = ""
        
        if ext == ".pdf":
            if PyPDF2 is None:
                raise ImportError("PyPDF2 is required for PDF processing. Install with: pip install PyPDF2")
            
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                    
        elif ext == ".docx":
            if docx is None:
                raise ImportError("python-docx is required for DOCX processing. Install with: pip install python-docx")
            
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        return text.strip()
        
    def process_uploaded_files(self, files: List[Any], session_id: str) -> Dict[str, Any]:
        """Process uploaded files and extract text content.
        
        Args:
            files: List of uploaded file objects.
            session_id: Session ID for this processing batch.
            
        Returns:
            Dictionary containing processing results.
        """
        if session_id not in self.sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
            
        session = self.sessions[session_id]
        processed_files = []
        
        for file in files:
            try:
                # Save uploaded file temporarily
                temp_path = self.temp_dir / f"{uuid.uuid4()}_{file.filename}"
                
                # Handle different file object types (FastAPI UploadFile vs others)
                if hasattr(file, 'read'):
                    content = file.read()
                    if hasattr(file, 'seek'):
                        file.seek(0)  # Reset file pointer
                else:
                    content = file
                    
                with open(temp_path, "wb") as temp_file:
                    temp_file.write(content)
                
                # Extract text
                extracted_text = self.extract_text(temp_path)
                
                # Store results
                file_info = {
                    "filename": file.filename if hasattr(file, 'filename') else str(temp_path.name),
                    "path": str(temp_path),
                    "text": extracted_text,
                    "size": len(extracted_text),
                    "processed_at": None  # Could add timestamp here
                }
                
                processed_files.append(file_info)
                session["documents"].append(file_info)
                session["extracted_texts"][file_info["filename"]] = extracted_text
                
                logger.info(f"Successfully processed file: {file_info['filename']}")
                
            except Exception as e:
                logger.error(f"Error processing file {getattr(file, 'filename', 'unknown')}: {e}")
                # Continue processing other files
                continue
                
        return {
            "session_id": session_id,
            "processed_files": len(processed_files),
            "total_text_length": sum(len(f["text"]) for f in processed_files),
            "files": processed_files
        }
        
    def get_session_documents(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a session.
        
        Args:
            session_id: Session ID.
            
        Returns:
            List of document information dictionaries.
        """
        if session_id not in self.sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
            
        return self.sessions[session_id]["documents"]
        
    def get_combined_text(self, session_id: str) -> str:
        """Get combined text from all documents in a session.
        
        Args:
            session_id: Session ID.
            
        Returns:
            Combined text from all documents.
        """
        if session_id not in self.sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
            
        texts = list(self.sessions[session_id]["extracted_texts"].values())
        return "\n\n".join(texts)
        
    def cleanup_session(self, session_id: str) -> None:
        """Clean up temporary files and session data.
        
        Args:
            session_id: Session ID to clean up.
        """
        if session_id not in self.sessions:
            return
            
        session = self.sessions[session_id]
        
        # Clean up temporary files
        for doc in session["documents"]:
            try:
                temp_path = Path(doc["path"])
                if temp_path.exists():
                    temp_path.unlink()
            except Exception as e:
                logger.warning(f"Could not delete temporary file {doc['path']}: {e}")
                
        # Remove session
        del self.sessions[session_id]
        logger.info(f"Cleaned up session: {session_id}") 