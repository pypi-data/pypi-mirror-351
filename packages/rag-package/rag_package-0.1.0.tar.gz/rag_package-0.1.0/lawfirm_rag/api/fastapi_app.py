"""
FastAPI application for LawFirm-RAG.

Provides REST API endpoints for document analysis and query generation.
"""

import os
import logging
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Security, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..core.document_processor import DocumentProcessor
from ..core.ai_engine import AIEngine
from ..core.query_generator import QueryGenerator
from ..core.model_downloader import ModelDownloader, ModelDownloadError
from ..core.model_manager import ModelManager
from ..utils.config import ConfigManager

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

# Global components
config_manager = ConfigManager()
doc_processor = DocumentProcessor()
ai_engine = None
query_generator = None
model_downloader = ModelDownloader()
model_manager = ModelManager()

# Initialize AI components
def initialize_ai_components():
    """Initialize AI engine and query generator."""
    global ai_engine, query_generator
    
    config = config_manager.get_config()
    model_path = config.get("model", {}).get("path")
    
    if model_path:
        model_path = Path(model_path).expanduser()
        if model_path.exists():
            ai_engine = AIEngine(str(model_path))
            if ai_engine.load_model():
                query_generator = QueryGenerator(ai_engine)
                logger.info("AI components initialized successfully")
            else:
                logger.warning("Failed to load AI model")
        else:
            logger.warning(f"Model file not found: {model_path}")
    
    # Fallback query generator without AI
    if not query_generator:
        query_generator = QueryGenerator()
        logger.info("Query generator initialized without AI model")

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

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    # Initialize AI components
    initialize_ai_components()

# Authentication dependency
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API key if authentication is enabled."""
    api_key = os.getenv("LAWFIRM_RAG_API_KEY")
    
    if api_key:
        if not credentials or credentials.credentials != api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key"
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

@app.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Upload and process documents."""
    try:
        # Create session
        session_id = doc_processor.create_session()
        
        # Process files
        file_data = []
        for file in files:
            content = await file.read()
            # Create a file-like object for processing
            class FileObj:
                def __init__(self, filename, content):
                    self.filename = filename
                    # Ensure content is bytes for writing to file
                    if isinstance(content, str):
                        self._content = content.encode('utf-8')
                    else:
                        self._content = content
                
                def read(self):
                    return self._content
                
                def seek(self, position):
                    pass  # No-op for our use case
            
            file_obj = FileObj(file.filename, content)
            file_data.append(file_obj)
        
        # Process uploaded files
        results = doc_processor.process_uploaded_files(file_data, session_id)
        
        return {
            "session_id": session_id,
            "processed_files": results["processed_files"],
            "total_text_length": results["total_text_length"],
            "files": [{"filename": f["filename"], "size": f["size"]} for f in results["files"]]
        }
        
    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_documents(
    request: AnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Analyze documents in a session."""
    try:
        # Get combined text from session
        text = doc_processor.get_combined_text(request.session_id)
        
        if not text:
            raise HTTPException(status_code=404, detail="Session not found or no documents")
        
        # Perform analysis
        if ai_engine and ai_engine.is_loaded:
            try:
                result = ai_engine.analyze_document(text, request.analysis_type)
                method = "ai"
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                result = _fallback_analysis(text, request.analysis_type)
                method = "fallback"
        else:
            result = _fallback_analysis(text, request.analysis_type)
            method = "fallback"
        
        return AnalysisResponse(
            session_id=request.session_id,
            analysis_type=request.analysis_type,
            result=result,
            method=method
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
        # Get combined text from session
        text = doc_processor.get_combined_text(request.session_id)
        
        if not text:
            raise HTTPException(status_code=404, detail="Session not found or no documents")
        
        # Generate queries
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
    """Get information about a session."""
    try:
        documents = doc_processor.get_session_documents(session_id)
        text = doc_processor.get_combined_text(session_id)
        
        return {
            "session_id": session_id,
            "document_count": len(documents),
            "total_text_length": len(text),
            "documents": [{"filename": doc["filename"], "size": doc["size"]} for doc in documents]
        }
        
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=404, detail="Session not found")

@app.delete("/sessions/{session_id}")
async def cleanup_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Clean up a session and its temporary files."""
    try:
        doc_processor.cleanup_session(session_id)
        return {"message": f"Session {session_id} cleaned up successfully"}
        
    except Exception as e:
        logger.error(f"Error cleaning up session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models(
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """List available AI models."""
    try:
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
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """List all available models for download with their current status."""
    try:
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
        success = model_downloader.download_model(model_variant, force=force)
        
        if success:
            logger.info(f"Successfully downloaded {model_variant}")
            # Reinitialize AI components if this is the first model
            global ai_engine, query_generator
            if not ai_engine or not ai_engine.is_loaded:
                initialize_ai_components()
        else:
            logger.error(f"Failed to download {model_variant}")
            
    except ModelDownloadError as e:
        logger.error(f"Model download error for {model_variant}: {e}")
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
        # Validate model variant
        if request.model_variant not in model_downloader.SUPPORTED_VARIANTS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported model variant: {request.model_variant}. "
                       f"Supported variants: {list(model_downloader.SUPPORTED_VARIANTS.keys())}"
            )
        
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
        progress = model_downloader.get_download_progress()
        
        return ModelProgressResponse(
            model_variant=progress["model_variant"],
            progress=progress["progress"],
            status=progress["status"],
            error=progress["error"],
            total_size=progress["total_size"],
            downloaded_size=progress["downloaded_size"],
            speed=progress["speed"],
            eta=progress["eta"]
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
            # Update global AI components
            global ai_engine, query_generator
            ai_engine = model_manager.get_active_model()
            if ai_engine and ai_engine.is_loaded:
                from ..core.query_generator import QueryGenerator
                query_generator = QueryGenerator(ai_engine)
            
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
        success = model_manager.unload_model(model_variant)
        
        if success:
            # Update global AI components if we unloaded the active model
            global ai_engine, query_generator
            active_model = model_manager.get_active_model()
            
            if active_model:
                ai_engine = active_model
                from ..core.query_generator import QueryGenerator
                query_generator = QueryGenerator(ai_engine)
            else:
                ai_engine = None
                query_generator = QueryGenerator()  # Fallback mode
            
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
        success = model_manager.switch_active_model(model_variant)
        
        if success:
            # Update global AI components
            global ai_engine, query_generator
            ai_engine = model_manager.get_active_model()
            if ai_engine and ai_engine.is_loaded:
                from ..core.query_generator import QueryGenerator
                query_generator = QueryGenerator(ai_engine)
            
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