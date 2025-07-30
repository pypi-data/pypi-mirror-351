"""
FastAPI application for LawFirm-RAG.

Provides REST API endpoints for document analysis and query generation.
"""

import os
import logging
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import uuid
import time

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Security, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# LAZY IMPORTS - Only import when needed to avoid 20-second startup delay
# from ..core.document_processor import DocumentProcessor
# from ..core.ai_engine import AIEngine, create_ai_engine_from_config
# from ..core.query_generator import QueryGenerator
# from ..core.model_downloader import ModelDownloader
# from ..core.model_manager import ModelManager
# from ..core.enhanced_document_processor import EnhancedDocumentProcessor

from ..utils.config import ConfigManager

# Vector Store imports - also made lazy
# try:
#     from ..core.vector_store import create_vector_store
#     VECTOR_STORE_AVAILABLE = True
# except ImportError as e:
#     VECTOR_STORE_AVAILABLE = False
#     logging.warning(f"Vector store not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LawFirm-RAG API",
    description="AI-Powered Legal Document Analysis API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Define public endpoints that don't require authentication
PUBLIC_ENDPOINTS = [
    "/",
    "/health", 
    "/app",
    "/vector-test",
    "/api/vector-store",
    "/models/available",
    "/docs",
    "/redoc",
    "/openapi.json"
]

# Global components - now initialized lazily
config_manager = ConfigManager()

# Lazy-loaded global components
_doc_processor = None
_ai_engine = None
_query_generator = None
_model_downloader = None
_model_manager = None
_enhanced_doc_processor = None
_vector_store = None
_vector_store_available = None

def get_doc_processor():
    """Lazy load document processor."""
    global _doc_processor
    if _doc_processor is None:
        from ..core.document_processor import DocumentProcessor
        _doc_processor = DocumentProcessor()
        logger.info("Document processor initialized")
    return _doc_processor

def get_enhanced_doc_processor():
    """Lazy load enhanced document processor."""
    global _enhanced_doc_processor
    if _enhanced_doc_processor is None:
        try:
            from ..core.enhanced_document_processor import EnhancedDocumentProcessor
            temp_dir = config_manager.get_temp_dir()
            _enhanced_doc_processor = EnhancedDocumentProcessor(
                temp_dir=str(temp_dir),
                chunk_size=1000,
                chunk_overlap=200,
                use_vector_db=True
            )
            logger.info("Enhanced document processor initialized")
        except Exception as e:
            logger.warning(f"Enhanced document processor failed to initialize: {e}")
            _enhanced_doc_processor = None
    return _enhanced_doc_processor

def get_ai_engine():
    """Lazy load AI engine."""
    global _ai_engine
    if _ai_engine is None:
        try:
            from ..core.ai_engine import create_ai_engine_from_config
            config = config_manager.get_config()
            _ai_engine = create_ai_engine_from_config(config)
            
            if _ai_engine and _ai_engine.load_model():
                logger.info("AI engine initialized successfully")
            else:
                logger.warning("Failed to load AI model")
                _ai_engine = None
        except Exception as e:
            logger.warning(f"Failed to initialize AI engine: {e}")
            _ai_engine = None
    return _ai_engine

def get_query_generator():
    """Lazy load query generator."""
    global _query_generator
    if _query_generator is None:
        try:
            from ..core.query_generator import QueryGenerator
            ai_engine = get_ai_engine()
            if ai_engine:
                _query_generator = QueryGenerator(ai_engine)
                logger.info("Query generator initialized with AI")
            else:
                _query_generator = QueryGenerator()
                logger.info("Query generator initialized without AI")
        except Exception as e:
            logger.warning(f"Failed to initialize query generator: {e}")
            from ..core.query_generator import QueryGenerator
            _query_generator = QueryGenerator()
    return _query_generator

def get_model_downloader():
    """Lazy load model downloader."""
    global _model_downloader
    if _model_downloader is None:
        from ..core.model_downloader import ModelDownloader
        _model_downloader = ModelDownloader()
        logger.info("Model downloader initialized")
    return _model_downloader

def get_model_manager():
    """Lazy load model manager."""
    global _model_manager
    if _model_manager is None:
        from ..core.model_manager import ModelManager
        _model_manager = ModelManager()
        logger.info("Model manager initialized")
    return _model_manager

def get_vector_store():
    """Lazy load vector store."""
    global _vector_store, _vector_store_available
    if _vector_store_available is None:
        try:
            from ..core.vector_store import create_vector_store
            _vector_store_available = True
        except ImportError as e:
            _vector_store_available = False
            logger.warning(f"Vector store not available: {e}")
            return None
    
    if _vector_store_available and _vector_store is None:
        try:
            from ..core.vector_store import create_vector_store
            _vector_store = create_vector_store("lawfirm_documents", "legal")
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.warning(f"Vector store failed to initialize: {e}")
            _vector_store = None
    
    return _vector_store

# Setup templates
templates_dir = Path(__file__).parent.parent / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files for frontend assets
web_static_path = Path(__file__).parent.parent / "web" / "static"
web_assets_path = web_static_path / "assets"

if web_assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(web_assets_path)), name="assets")
    logger.info(f"Mounted static assets from: {web_assets_path}")
else:
    logger.warning(f"Web assets directory not found: {web_assets_path}")

# Mount the main static directory for other static files
if web_static_path.exists():
    app.mount("/static", StaticFiles(directory=str(web_static_path)), name="static")
    logger.info(f"Static files mounted: assets from {web_assets_path}, static from {web_static_path}")
else:
    logger.warning(f"Web static directory not found: {web_static_path}")

# Initialize on startup (non-blocking with lazy loading)
@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    logger.info("FastAPI app started with lazy loading enabled")

# Authentication dependency
async def verify_api_key(request: Request, credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API key if authentication is enabled, with support for public endpoints."""
    api_key = os.getenv("LAWFIRM_RAG_API_KEY")
    
    # If no API key is configured, allow all requests
    if not api_key:
        return credentials
    
    # Check if the current endpoint is public
    request_path = request.url.path
    for public_endpoint in PUBLIC_ENDPOINTS:
        if request_path == public_endpoint or request_path.startswith(public_endpoint):
            return credentials
    
    # For protected endpoints, verify the API key
    if not credentials or credentials.credentials != api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    
    return credentials

# Optional authentication dependency for public endpoints
async def optional_verify_api_key(request: Request, credentials: HTTPAuthorizationCredentials = Security(security)):
    """Optional authentication for endpoints that can work with or without API keys."""
    api_key = os.getenv("LAWFIRM_RAG_API_KEY")
    
    # If no API key is configured, allow all requests
    if not api_key:
        return credentials
    
    # If credentials are provided, verify them
    if credentials and credentials.credentials != api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return credentials

# Pydantic models
class AnalysisRequest(BaseModel):
    session_id: str
    analysis_type: str = "summary"

class QueryRequest(BaseModel):
    session_id: str
    database: str = "westlaw"
    all_databases: bool = False

class AnalysisResponse(BaseModel):
    session_id: str
    analysis_type: str
    result: str
    method: str

class QueryResponse(BaseModel):
    session_id: str
    database: str
    query: str
    confidence: float
    suggestions: List[str]

# Model download models
class ModelDownloadRequest(BaseModel):
    model_variant: str
    force: bool = False

class ModelDownloadResponse(BaseModel):
    message: str
    model_variant: str
    status: str
    download_started: bool

class ModelProgressResponse(BaseModel):
    model_variant: Optional[str]
    progress: float
    status: str
    error: Optional[str]
    total_size: int
    downloaded_size: int
    speed: float
    eta: Optional[float]

class ModelListResponse(BaseModel):
    available_models: Dict[str, Dict]
    download_status: Dict

# Model loading models
class ModelLoadRequest(BaseModel):
    model_variant: str
    force_reload: bool = False

class ModelLoadResponse(BaseModel):
    message: str
    model_variant: str
    status: str
    loaded: bool

class LoadedModelInfo(BaseModel):
    model_variant: str
    model_path: str
    loaded_at: str
    memory_usage: Optional[int] = None
    is_active: bool

class LoadedModelsResponse(BaseModel):
    loaded_models: List[LoadedModelInfo]
    active_model: Optional[str]
    total_memory_usage: Optional[int]

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LawFirm-RAG API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Use lazy loaders - these will only load when first accessed
    model_manager = get_model_manager()
    query_generator = get_query_generator()
    
    active_model = model_manager.get_active_model()
    status = model_manager.get_status()
    
    return {
        "status": "healthy",
        "ai_engine_loaded": active_model is not None and active_model.is_loaded if active_model else False,
        "query_generator_available": query_generator is not None,
        "loaded_models_count": status["loaded_models_count"],
        "active_model": status["active_model"],
        "available_models": status["available_models"]
    }

@app.get("/app")
async def serve_frontend():
    """Serve the frontend application."""
    frontend_html = Path(__file__).parent.parent / "web" / "static" / "index.html"
    if frontend_html.exists():
        return FileResponse(str(frontend_html))
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")

@app.post("/create-collection")
async def create_collection(
    request: dict,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Create a new document collection."""
    try:
        enhanced_doc_processor = get_enhanced_doc_processor()
        if not enhanced_doc_processor:
            raise HTTPException(status_code=500, detail="Document processor not available")
            
        name = request.get("name", f"collection_{uuid.uuid4().hex[:8]}")
        description = request.get("description", "")
        
        collection_id = enhanced_doc_processor.create_collection(name, description)
        
        return {
            "collection_id": collection_id,
            "name": name,
            "description": description,
            "status": "created"
        }
        
    except Exception as e:
        logger.error(f"Failed to create collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections")
async def list_collections(
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """List all document collections."""
    try:
        enhanced_doc_processor = get_enhanced_doc_processor()
        if not enhanced_doc_processor:
            return {"collections": []}
            
        collections = enhanced_doc_processor.list_collections()
        return {"collections": collections}
        
    except Exception as e:
        logger.error(f"Failed to list collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    collection_id: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Upload and process documents with enhanced processing."""
    try:
        # Use enhanced processor if available
        enhanced_doc_processor = get_enhanced_doc_processor()
        if enhanced_doc_processor:
            # Create collection if not provided
            if not collection_id:
                collection_id = enhanced_doc_processor.create_collection(
                    name=f"Upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    description="Auto-created collection from file upload"
                )
            
            # Process files with enhanced processor
            file_data = []
            for file in files:
                content = await file.read()
                
                class FileObj:
                    def __init__(self, filename, content):
                        self.filename = filename
                        self._content = content if isinstance(content, bytes) else content.encode('utf-8')
                    
                    def read(self):
                        return self._content
                    
                    def seek(self, position):
                        pass
                
                file_obj = FileObj(file.filename, content)
                file_data.append(file_obj)
            
            # Process with enhanced processor
            results = enhanced_doc_processor.process_uploaded_files(file_data, collection_id)
            
            return {
                "session_id": collection_id,  # Frontend expects session_id
                "collection_id": collection_id,
                "file_count": results["processed_documents"],  # Frontend expects file_count
                "processed_documents": results["processed_documents"],
                "total_chunks": results["total_chunks"],
                "total_text_length": results["total_text_length"],
                "files": [
                    {
                        "filename": doc["filename"],
                        "document_type": doc["metadata"].get("document_type", "unknown"),
                        "chunks": len(doc["chunks"]),
                        "word_count": doc["metadata"].get("word_count", 0)
                    } 
                    for doc in results["documents"]
                ],
                "errors": results["errors"],
                "status": "Uploaded",  # Frontend expects status
                "enhanced": True
            }
        
        else:
            # Fallback to original session-based approach
            doc_processor = get_doc_processor()
            if not collection_id:
                collection_id = doc_processor.create_session()
            
            file_data = []
            for file in files:
                content = await file.read()
                
                class FileObj:
                    def __init__(self, filename, content):
                        self.filename = filename
                        if isinstance(content, str):
                            self._content = content.encode('utf-8')
                        else:
                            self._content = content
                    
                    def read(self):
                        return self._content
                    
                    def seek(self, position):
                        pass
                
                file_obj = FileObj(file.filename, content)
                file_data.append(file_obj)
            
            results = doc_processor.process_uploaded_files(file_data, collection_id)
            
            return {
                "session_id": collection_id,  # Frontend expects session_id
                "collection_id": collection_id,  # Using session_id as collection_id
                "file_count": results["processed_files"],  # Frontend expects file_count
                "processed_files": results["processed_files"],
                "total_text_length": results["total_text_length"],
                "files": [{"filename": f["filename"], "size": f["size"]} for f in results["files"]],
                "status": "Uploaded",  # Frontend expects status
                "enhanced": False
            }
        
    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_documents(
    request: AnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Analyze documents in a collection with enhanced processing."""
    try:
        text = ""
        
        # Try enhanced processor first
        enhanced_doc_processor = get_enhanced_doc_processor()
        if enhanced_doc_processor:
            try:
                # Use the new get_combined_text method
                text = enhanced_doc_processor.get_combined_text(request.session_id)
            except ValueError:
                # Collection not found in enhanced processor, try fallback
                doc_processor = get_doc_processor()
                if hasattr(doc_processor, 'get_combined_text'):
                    try:
                        text = doc_processor.get_combined_text(request.session_id)
                    except:
                        pass
        
        if not text:
            raise HTTPException(status_code=404, detail="Session/Collection not found or no documents")
        
        # Use AI model if available
        ai_engine = get_ai_engine()
        if ai_engine and ai_engine.is_loaded:
            try:
                result = ai_engine.analyze_document(text, request.analysis_type)
                return AnalysisResponse(
                    session_id=request.session_id,
                    analysis_type=request.analysis_type,
                    result=result,
                    method="ai_model"
                )
            except Exception as e:
                logger.warning(f"AI analysis failed, using fallback: {e}")
        
        # Fallback to simple analysis
        result = _fallback_analysis(text, request.analysis_type)
        return AnalysisResponse(
            session_id=request.session_id,
            analysis_type=request.analysis_type,
            result=result,
            method="fallback"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def generate_query(
    request: QueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Generate search queries for legal databases."""
    try:
        # Get combined text from collection or session
        text = ""
        
        # Try enhanced processor first
        enhanced_doc_processor = get_enhanced_doc_processor()
        if enhanced_doc_processor:
            try:
                text = enhanced_doc_processor.get_combined_text(request.session_id)
            except ValueError:
                # Collection not found, try fallback
                pass
        
        # Fall back to original session-based processor
        if not text:
            doc_processor = get_doc_processor()
            if hasattr(doc_processor, 'get_combined_text'):
                try:
                    text = doc_processor.get_combined_text(request.session_id)
                except:
                    pass
        
        if not text:
            raise HTTPException(status_code=404, detail="Session/Collection not found or no documents")
        
        # Generate queries
        query_generator = get_query_generator()
        if request.all_databases:
            results = query_generator.generate_multiple_queries(text)
            return {"session_id": request.session_id, "queries": results}
        else:
            result = query_generator.generate_query(text, request.database)
            return {
                "session_id": request.session_id,
                "database": request.database,
                "query": result["query"],
                "confidence": result["confidence"],
                "suggestions": result["suggestions"]
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Get information about a session or collection."""
    try:
        # Try enhanced processor first
        enhanced_doc_processor = get_enhanced_doc_processor()
        if enhanced_doc_processor:
            try:
                collection_info = enhanced_doc_processor.get_collection_info(session_id)
                documents = enhanced_doc_processor.get_collection_documents(session_id)
                
                return {
                    "session_id": session_id,
                    "collection_id": session_id,
                    "document_count": len(documents),
                    "documents": [
                        {
                            "filename": doc.filename,
                            "document_type": doc.metadata.get("document_type", "unknown"),
                            "word_count": doc.metadata.get("word_count", 0),
                            "chunks": len(doc.chunks)
                        }
                        for doc in documents
                    ],
                    "total_text_length": sum(doc.get_total_length() for doc in documents),
                    "created_at": collection_info.get("created_at"),
                    "enhanced": True
                }
            except ValueError:
                pass
        
        # Fall back to original session approach
        doc_processor = get_doc_processor()
        if hasattr(doc_processor, 'get_session_documents'):
            documents = doc_processor.get_session_documents(session_id)
            text = doc_processor.get_combined_text(session_id)
            
            return {
                "session_id": session_id,
                "document_count": len(documents),
                "total_text_length": len(text),
                "enhanced": False
            }
        
        raise HTTPException(status_code=404, detail="Session/Collection not found")
        
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=404, detail="Session not found")

@app.delete("/sessions/{session_id}")
async def cleanup_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Clean up a session or collection."""
    try:
        # Try enhanced processor first
        enhanced_doc_processor = get_enhanced_doc_processor()
        if enhanced_doc_processor:
            try:
                enhanced_doc_processor.cleanup_collection(session_id)
                return {"message": f"Collection {session_id} cleaned up successfully", "enhanced": True}
            except ValueError:
                pass
        
        # Fall back to original session cleanup
        doc_processor = get_doc_processor()
        if hasattr(doc_processor, 'cleanup_session'):
            doc_processor.cleanup_session(session_id)
            return {"message": f"Session {session_id} cleaned up successfully", "enhanced": False}
        
        raise HTTPException(status_code=404, detail="Session/Collection not found")
        
    except Exception as e:
        logger.error(f"Error cleaning up session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models(
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """List available AI models."""
    try:
        model_manager = get_model_manager()
        available = model_manager.discover_models()
        loaded = model_manager.get_loaded_models()
        status = model_manager.get_status()
        
        return {
            "available": available,
            "loaded": loaded,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/available", response_model=ModelListResponse)
async def list_available_models(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(optional_verify_api_key)
):
    """List all available models for download with their current status."""
    try:
        model_downloader = get_model_downloader()
        available_models = model_downloader.list_available_models()
        download_status = model_downloader.get_download_progress()
        
        return ModelListResponse(
            available_models=available_models,
            download_status=download_status
        )
        
    except Exception as e:
        logger.error(f"Error listing available models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _download_model_background(model_variant: str, force: bool = False):
    """Background task to download a model."""
    try:
        logger.info(f"Starting background download of {model_variant}")
        model_downloader = get_model_downloader()
        success = model_downloader.download_model(model_variant, force=force)
        
        if success:
            logger.info(f"Successfully downloaded {model_variant}")
        else:
            logger.error(f"Failed to download {model_variant}")
            
    except Exception as e:
        logger.error(f"Unexpected error downloading {model_variant}: {e}")

@app.post("/models/download", response_model=ModelDownloadResponse)
async def download_model(
    request: ModelDownloadRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Start downloading a model from Hugging Face."""
    try:
        # Basic validation - just check it's not empty
        if not request.model_variant or not request.model_variant.strip():
            raise HTTPException(
                status_code=400,
                detail="Model variant cannot be empty"
            )
        
        model_downloader = get_model_downloader()
        
        # Check if already downloaded
        if not request.force and model_downloader.is_model_downloaded(request.model_variant):
            return ModelDownloadResponse(
                message=f"Model {request.model_variant} is already downloaded",
                model_variant=request.model_variant,
                status="already_downloaded",
                download_started=False
            )
        
        # Check if download is already in progress
        current_progress = model_downloader.get_download_progress()
        if current_progress["status"] == "downloading":
            if current_progress["model_variant"] == request.model_variant:
                return ModelDownloadResponse(
                    message=f"Download of {request.model_variant} is already in progress",
                    model_variant=request.model_variant,
                    status="already_downloading",
                    download_started=False
                )
            else:
                raise HTTPException(
                    status_code=409,
                    detail=f"Another model ({current_progress['model_variant']}) is currently downloading"
                )
        
        # Start download in background
        background_tasks.add_task(_download_model_background, request.model_variant, request.force)
        
        return ModelDownloadResponse(
            message=f"Download of {request.model_variant} started successfully",
            model_variant=request.model_variant,
            status="download_started",
            download_started=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting model download: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/download-progress", response_model=ModelProgressResponse)
async def get_download_progress(
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Get the current download progress."""
    try:
        model_downloader = get_model_downloader()
        progress = model_downloader.get_download_progress()
        
        return ModelProgressResponse(
            model_variant=progress.get("model_variant"),
            progress=progress.get("progress", 0.0),
            status=progress.get("status", "idle"),
            error=progress.get("error"),
            total_size=progress.get("total_size", 0),
            downloaded_size=progress.get("downloaded_size", 0),
            speed=progress.get("speed", 0.0),
            eta=progress.get("eta")
        )
        
    except Exception as e:
        logger.error(f"Error getting download progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/cancel-download")
async def cancel_download(
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Cancel the current model download."""
    try:
        model_downloader = get_model_downloader()
        success = model_downloader.cancel_download()
        
        if success:
            return {"message": "Download cancelled successfully", "cancelled": True}
        else:
            return {"message": "No active download to cancel", "cancelled": False}
            
    except Exception as e:
        logger.error(f"Error cancelling download: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/models/cleanup")
async def cleanup_failed_downloads(
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Clean up any failed or temporary download files."""
    try:
        model_downloader = get_model_downloader()
        cleaned_count = model_downloader.cleanup_failed_downloads()
        
        return {
            "message": f"Cleaned up {cleaned_count} temporary files",
            "files_cleaned": cleaned_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up downloads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Model Loading Endpoints

@app.get("/models/loaded", response_model=LoadedModelsResponse)
async def get_loaded_models(
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Get information about currently loaded models."""
    try:
        model_manager = get_model_manager()
        loaded_models = model_manager.get_loaded_models()
        status = model_manager.get_status()
        
        return LoadedModelsResponse(
            loaded_models=[
                LoadedModelInfo(
                    model_variant=model["model_variant"],
                    model_path=model["model_path"],
                    loaded_at=model["loaded_at"],
                    memory_usage=model.get("memory_usage"),
                    is_active=model["is_active"]
                ) for model in loaded_models
            ],
            active_model=status["active_model"],
            total_memory_usage=status["total_memory_usage"]
        )
        
    except Exception as e:
        logger.error(f"Error getting loaded models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/load", response_model=ModelLoadResponse)
async def load_model(
    request: ModelLoadRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Load a downloaded model into memory."""
    try:
        model_manager = get_model_manager()
        
        # Validate that the model exists and is downloaded
        available_models = model_manager.discover_models()
        
        if request.model_variant not in available_models:
            raise HTTPException(
                status_code=404,
                detail=f"Model {request.model_variant} not found or not downloaded. "
                       f"Available models: {list(available_models.keys())}"
            )
        
        # Load the model
        success = model_manager.load_model(request.model_variant, request.force_reload)
        
        if success:
            return ModelLoadResponse(
                message=f"Model {request.model_variant} loaded successfully",
                model_variant=request.model_variant,
                status="loaded",
                loaded=True
            )
        else:
            return ModelLoadResponse(
                message=f"Failed to load model {request.model_variant}",
                model_variant=request.model_variant,
                status="failed",
                loaded=False
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/unload")
async def unload_model(
    model_variant: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Unload a model from memory."""
    try:
        model_manager = get_model_manager()
        success = model_manager.unload_model(model_variant)
        
        if success:
            return {
                "message": f"Model {model_variant} unloaded successfully",
                "model_variant": model_variant,
                "status": "unloaded"
            }
        else:
            return {
                "message": f"Failed to unload model {model_variant} (may not be loaded)",
                "model_variant": model_variant,
                "status": "not_loaded"
            }
        
    except Exception as e:
        logger.error(f"Error unloading model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/switch")
async def switch_active_model(
    model_variant: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Switch the active model without unloading others."""
    try:
        model_manager = get_model_manager()
        success = model_manager.switch_active_model(model_variant)
        
        if success:
            return {
                "message": f"Switched to model {model_variant}",
                "model_variant": model_variant,
                "status": "active"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Model {model_variant} is not loaded"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _fallback_analysis(text: str, analysis_type: str) -> str:
    """Provide basic analysis when AI model is not available."""
    words = text.split()
    sentences = text.split('.')
    
    if analysis_type == "summary":
        summary_sentences = sentences[:3]
        return ". ".join(s.strip() for s in summary_sentences if s.strip()) + "."
        
    elif analysis_type == "key_points":
        legal_terms = ["contract", "agreement", "liability", "negligence", "breach"]
        found_terms = [term.title() for term in legal_terms if term in text.lower()]
        
        if found_terms:
            return "• " + "\n• ".join(f"Document mentions: {term}" for term in found_terms[:5])
        else:
            return f"• Document contains legal content\n• Length: {len(words)} words\n• {len(sentences)} sentences"
            
    elif analysis_type == "legal_issues":
        issues = []
        text_lower = text.lower()
        
        if "contract" in text_lower or "agreement" in text_lower:
            issues.append("Contract Law")
        if "negligence" in text_lower or "liability" in text_lower:
            issues.append("Tort Law")
        if "court" in text_lower or "litigation" in text_lower:
            issues.append("Civil Procedure")
            
        if issues:
            return "Potential legal areas:\n• " + "\n• ".join(issues)
        else:
            return "Legal document requiring professional analysis"
    
    return f"Basic analysis: {len(words)} words, {len(sentences)} sentences"

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Vector Store API Endpoints
class VectorStoreAddRequest(BaseModel):
    text: str
    metadata: Optional[Dict] = None

class VectorStoreSearchRequest(BaseModel):
    query: str
    n_results: int = 10
    filter_metadata: Optional[Dict] = None

# Bulk upload progress tracking
UPLOAD_PROGRESS = {}

class BulkUploadRequest(BaseModel):
    collection_name: str
    description: Optional[str] = None
    batch_size: int = 50
    add_to_vector_store: bool = False

class UploadProgressResponse(BaseModel):
    upload_id: str
    status: str  # "processing", "completed", "failed", "cancelled"
    total_files: int
    processed_files: int
    failed_files: int
    current_file: Optional[str] = None
    progress_percentage: float
    estimated_remaining_seconds: Optional[float] = None
    vector_store_progress: Optional[Dict] = None
    errors: List[str] = []

async def _process_bulk_upload_background(
    upload_id: str,
    files_data: List[Tuple[str, bytes]],  # (filename, content)
    collection_name: str,
    description: str,
    batch_size: int,
    add_to_vector_store: bool
):
    """Background task to process uploaded files."""
    
    try:
        start_time = time.time()
        
        UPLOAD_PROGRESS[upload_id] = {
            "status": "processing",
            "total_files": len(files_data),
            "processed_files": 0,
            "failed_files": 0,
            "current_file": None,
            "progress_percentage": 0.0,
            "estimated_remaining_seconds": None,
            "vector_store_progress": None,
            "errors": [],
            "start_time": start_time
        }
        
        # Get processors using lazy loading
        enhanced_doc_processor = get_enhanced_doc_processor()
        doc_processor = get_doc_processor()
        
        # Create collection
        if enhanced_doc_processor:
            collection_id = enhanced_doc_processor.create_collection(
                name=collection_name,
                description=description
            )
        else:
            collection_id = doc_processor.create_session()
            
        processed_docs = []
        
        # Process files in batches
        for i, (filename, content) in enumerate(files_data):
            # Check for cancellation
            if UPLOAD_PROGRESS[upload_id]["status"] == "cancelled":
                break
                
            UPLOAD_PROGRESS[upload_id]["current_file"] = filename
            
            try:
                # Create file object
                class FileObj:
                    def __init__(self, filename, content):
                        self.filename = filename
                        self._content = content if isinstance(content, bytes) else content.encode('utf-8')
                    
                    def read(self):
                        return self._content
                    
                    def seek(self, position):
                        pass
                
                file_obj = FileObj(filename, content)
                
                if enhanced_doc_processor:
                    # Process with enhanced processor
                    result = enhanced_doc_processor.process_uploaded_files([file_obj], collection_id)
                    if result["processed_documents"] > 0:
                        processed_docs.extend(result["documents"])
                else:
                    # Fallback processing
                    result = doc_processor.process_uploaded_files([file_obj], collection_id)
                
                UPLOAD_PROGRESS[upload_id]["processed_files"] += 1
                
            except Exception as e:
                UPLOAD_PROGRESS[upload_id]["failed_files"] += 1
                UPLOAD_PROGRESS[upload_id]["errors"].append(f"{filename}: {str(e)}")
                logger.error(f"Failed to process {filename}: {e}")
            
            # Update progress
            processed = UPLOAD_PROGRESS[upload_id]["processed_files"]
            failed = UPLOAD_PROGRESS[upload_id]["failed_files"]
            total = UPLOAD_PROGRESS[upload_id]["total_files"]
            
            UPLOAD_PROGRESS[upload_id]["progress_percentage"] = ((processed + failed) / total) * 100
            
            # Estimate remaining time
            elapsed = time.time() - start_time
            if processed > 0:
                avg_time_per_file = elapsed / (processed + failed)
                remaining_files = total - processed - failed
                UPLOAD_PROGRESS[upload_id]["estimated_remaining_seconds"] = avg_time_per_file * remaining_files
        
        # Add to vector store if requested
        vector_store = get_vector_store()
        if add_to_vector_store and processed_docs and vector_store:
            UPLOAD_PROGRESS[upload_id]["vector_store_progress"] = {
                "status": "processing",
                "total_documents": len(processed_docs),
                "processed_documents": 0
            }
            
            try:
                # Extract texts and metadata from processed documents
                texts = []
                metadatas = []
                
                for doc_data in processed_docs:
                    # Combine all chunks for each document
                    # Enhanced processor uses 'content' field, not 'text'
                    combined_text = "\n\n".join([chunk["content"] for chunk in doc_data["chunks"]])
                    texts.append(combined_text)
                    
                    # Sanitize metadata for ChromaDB (no lists allowed)
                    sanitized_metadata = {}
                    for key, value in doc_data["metadata"].items():
                        if isinstance(value, list):
                            # Convert lists to comma-separated strings
                            sanitized_metadata[key] = ", ".join(str(item) for item in value)
                        elif isinstance(value, (str, int, float, bool)):
                            sanitized_metadata[key] = value
                        else:
                            # Convert other types to string
                            sanitized_metadata[key] = str(value)
                    
                    metadatas.append(sanitized_metadata)
                
                # Progress callback for vector store operations
                def vector_progress_callback(processed, total, batch_num):
                    if upload_id in UPLOAD_PROGRESS:
                        UPLOAD_PROGRESS[upload_id]["vector_store_progress"]["processed_documents"] = processed
                        logger.info(f"Vector store progress: {processed}/{total} documents (batch {batch_num})")
                
                # Add to vector store in batches
                batch_size_vector = min(batch_size, 50)  # Vector store batch size
                added_ids = vector_store.add_documents(
                    texts=texts,
                    metadatas=metadatas,
                    batch_size=batch_size_vector,
                    progress_callback=vector_progress_callback
                )
                
                UPLOAD_PROGRESS[upload_id]["vector_store_progress"]["status"] = "completed"
                UPLOAD_PROGRESS[upload_id]["vector_store_progress"]["added_ids"] = added_ids
                
            except Exception as e:
                UPLOAD_PROGRESS[upload_id]["vector_store_progress"]["status"] = "failed"
                UPLOAD_PROGRESS[upload_id]["vector_store_progress"]["error"] = str(e)
                logger.error(f"Failed to add documents to vector store: {e}")
        
        # Mark as completed
        UPLOAD_PROGRESS[upload_id]["status"] = "completed"
        UPLOAD_PROGRESS[upload_id]["current_file"] = None
        
    except Exception as e:
        UPLOAD_PROGRESS[upload_id]["status"] = "failed"
        UPLOAD_PROGRESS[upload_id]["errors"].append(f"Fatal error: {str(e)}")
        logger.error(f"Bulk upload {upload_id} failed: {e}")

@app.post("/api/bulk-upload", response_model=Dict)
async def start_bulk_upload(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    collection_name: str = "bulk_upload",
    description: str = "Bulk uploaded documents",
    batch_size: int = 50,
    add_to_vector_store: bool = True,
    credentials: HTTPAuthorizationCredentials = Depends(optional_verify_api_key)
):
    """Start a bulk upload operation with progress tracking."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10000:  # Reasonable limit
        raise HTTPException(status_code=400, detail="Too many files (max 10,000)")
    
    # Generate upload ID
    upload_id = str(uuid.uuid4())
    
    try:
        # Read all files into memory (for smaller batches)
        # For very large uploads, you'd want to stream this differently
        files_data = []
        for file in files:
            content = await file.read()
            files_data.append((file.filename, content))
        
        # Add unique timestamp to collection name
        timestamped_name = f"{collection_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Start background processing
        background_tasks.add_task(
            _process_bulk_upload_background,
            upload_id,
            files_data,
            timestamped_name,
            description,
            batch_size,
            add_to_vector_store
        )
        
        return {
            "upload_id": upload_id,
            "message": f"Bulk upload started for {len(files)} files",
            "collection_name": timestamped_name,
            "add_to_vector_store": add_to_vector_store,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Failed to start bulk upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bulk-upload/progress/{upload_id}", response_model=UploadProgressResponse)
async def get_bulk_upload_progress(
    upload_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(optional_verify_api_key)
):
    """Get progress of a bulk upload operation."""
    if upload_id not in UPLOAD_PROGRESS:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    progress = UPLOAD_PROGRESS[upload_id]
    
    return UploadProgressResponse(
        upload_id=upload_id,
        status=progress["status"],
        total_files=progress["total_files"],
        processed_files=progress["processed_files"],
        failed_files=progress["failed_files"],
        current_file=progress["current_file"],
        progress_percentage=progress["progress_percentage"],
        estimated_remaining_seconds=progress.get("estimated_remaining_seconds"),
        vector_store_progress=progress.get("vector_store_progress"),
        errors=progress["errors"]
    )

@app.delete("/api/bulk-upload/{upload_id}")
async def cancel_bulk_upload(
    upload_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(optional_verify_api_key)
):
    """Cancel a bulk upload operation."""
    if upload_id not in UPLOAD_PROGRESS:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    UPLOAD_PROGRESS[upload_id]["status"] = "cancelled"
    
    return {
        "message": f"Upload {upload_id} cancellation requested",
        "status": "cancelled"
    }

@app.get("/api/bulk-upload/list")
async def list_bulk_uploads(
    credentials: HTTPAuthorizationCredentials = Depends(optional_verify_api_key)
):
    """List all bulk upload operations and their status."""
    return {
        "uploads": [
            {
                "upload_id": upload_id,
                "status": progress["status"],
                "total_files": progress["total_files"],
                "processed_files": progress["processed_files"],
                "failed_files": progress["failed_files"],
                "progress_percentage": progress["progress_percentage"]
            }
            for upload_id, progress in UPLOAD_PROGRESS.items()
        ]
    }

@app.get("/vector-test", response_class=HTMLResponse)
async def vector_test_page(request: Request):
    """Serve the vector store test interface."""
    vector_store = get_vector_store()
    if not vector_store:
        return HTMLResponse(
            content="<h1>Vector Store Not Available</h1><p>ChromaDB and sentence-transformers are required.</p>",
            status_code=503
        )
    
    return templates.TemplateResponse("vector_test.html", {"request": request})

@app.post("/api/vector-store/add")
async def add_document_to_vector_store(
    request: VectorStoreAddRequest,
    credentials: HTTPAuthorizationCredentials = Depends(optional_verify_api_key)
):
    """Add a document to the vector store."""
    vector_store = get_vector_store()
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not available")
    
    try:
        doc_id = vector_store.add_document(
            text=request.text,
            metadata=request.metadata
        )
        
        return {
            "doc_id": doc_id,
            "message": "Document added successfully"
        }
        
    except Exception as e:
        logger.error(f"Error adding document to vector store: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vector-store/search")
async def search_vector_store(
    query: str,
    n_results: int = 10,
    filter_metadata: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(optional_verify_api_key)
):
    """Search documents in the vector store."""
    vector_store = get_vector_store()
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not available")
    
    try:
        # Parse filter metadata if provided
        parsed_filter = None
        if filter_metadata:
            import json
            try:
                parsed_filter = json.loads(filter_metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid filter_metadata JSON")
        
        results = vector_store.search(
            query=query,
            n_results=n_results,
            filter_metadata=parsed_filter
        )
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching vector store: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vector-store/stats")
async def get_vector_store_stats(
    credentials: HTTPAuthorizationCredentials = Depends(optional_verify_api_key)
):
    """Get vector store statistics."""
    vector_store = get_vector_store()
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not available")
    
    try:
        stats = vector_store.get_collection_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting vector store stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/vector-store/clear")
async def clear_vector_store(
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Clear all documents from the vector store."""
    vector_store = get_vector_store()
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not available")
    
    try:
        success = vector_store.clear_collection()
        if success:
            return {"message": "Vector store cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear vector store")
        
    except Exception as e:
        logger.error(f"Error clearing vector store: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 