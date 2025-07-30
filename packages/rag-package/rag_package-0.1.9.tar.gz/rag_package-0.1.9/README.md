# LawFirm RAG Package 🎉

A comprehensive, **production-ready** Python package for legal document analysis and query generation using Retrieval-Augmented Generation (RAG) with local AI models. Features enterprise-grade document processing, vector search, and bulk upload capabilities.

## ✅ Current Status: FULLY FUNCTIONAL

The system is **complete and working end-to-end** with all major features implemented and tested:
- ✅ **Bulk Document Upload**: Process 1000+ documents with real-time progress tracking
- ✅ **Vector Search**: Semantic similarity search across all documents  
- ✅ **AI Analysis**: Document summarization and legal issue identification
- ✅ **Query Generation**: Sophisticated legal database queries (Westlaw, LexisNexis)
- ✅ **Multi-Format Support**: PDF, DOCX, TXT, JSON with advanced text extraction
- ✅ **ChromaDB Integration**: Enterprise-grade vector database with automatic management
- ✅ **PyTorch Compatibility**: All embedding system issues resolved
- ✅ **Web & CLI Interface**: Complete user interfaces for all operations

## 🚀 Key Features

### 📄 **Advanced Document Processing**
- **Multi-Library PDF Extraction**: pdfplumber, PyMuPDF, PyPDF2 with intelligent fallback
- **Format Support**: PDF, DOCX, TXT, JSON with structured text extraction
- **Bulk Upload**: Process thousands of files with progress tracking
- **Smart Chunking**: Configurable text chunking for optimal processing
- **Metadata Extraction**: Automatic metadata extraction and sanitization

### 🤖 **Enterprise AI Integration**
- **Local Models**: Full support for llama-cpp-python and Ollama backends
- **Model Management**: Automatic Hugging Face model downloading
- **Multiple Backends**: Flexible LLM abstraction layer
- **Legal Expertise**: Optimized prompts for legal document analysis
- **Fallback Support**: Graceful degradation when models unavailable

### 🔍 **Vector Search & RAG**
- **ChromaDB Integration**: Enterprise-grade vector database
- **Sentence Transformers**: Local embedding generation (384-dimensional)
- **Unified Search**: Search across all document sources in single interface
- **Metadata Filtering**: Advanced filtering by document type, date, etc.
- **Performance**: Sub-second search on large document collections

### 🌐 **Complete User Interfaces**
- **Modern Web UI**: React-based interface with drag-drop upload
- **REST API**: Comprehensive API with OpenAPI documentation
- **CLI Tools**: Full command-line interface for automation
- **Progress Tracking**: Real-time upload and processing progress
- **Authentication**: Optional API key authentication

### 💾 **Production Features**
- **Pip Installable**: `pip install lawfirm-rag-package`
- **Cross-Platform**: Windows, macOS, Linux support
- **Error Handling**: Comprehensive error handling with automatic recovery
- **Logging**: Detailed logging for monitoring and debugging
- **Configuration**: Flexible YAML/TOML configuration management

## 🚀 Installation

### Prerequisites
- **Python 3.11+** (Required for AI/ML dependencies)
- Windows, macOS, or Linux
- 4GB+ RAM recommended

### Quick Install

#### Single Python Version
```bash
pip install rag-package
rag setup
rag serve
```

#### Multiple Python Versions Installed

**Windows (Recommended):**
```bash
# Use Python Launcher to specify version
py -3.11 -m pip install rag-package
py -3.11 -m rag setup
py -3.11 -m rag serve
```

**macOS/Linux:**
```bash
# Use specific Python version
python3.11 -m pip install rag-package
python3.11 -m rag setup
python3.11 -m rag serve
```

**Alternative: Virtual Environment (All Platforms):**
```bash
# Create environment with Python 3.11
py -3.11 -m venv rag-env          # Windows
python3.11 -m venv rag-env        # macOS/Linux

# Activate environment
rag-env\Scripts\activate           # Windows
source rag-env/bin/activate       # macOS/Linux

# Install normally
pip install rag-package
rag setup
rag serve
```

### Verification
```bash
rag --version
```

## 🚀 Quick Start

### 💻 Professional Installation & Setup

```bash
# 1. Install the RAG CLI tool (requires Python 3.11+)
pip install rag-package

# 2. Set up isolated environment with all AI/ML dependencies  
rag setup

# 3. Start the web interface
rag serve

# 🎉 Your browser opens automatically to http://localhost:8000
#    Upload documents and start analyzing!
```

**Why the setup step?** This AI/ML package requires specific versions of PyTorch, ChromaDB, and other dependencies. The `rag setup` command creates an isolated environment to prevent conflicts with your other Python projects.

### ⚡ What You Get
- **Isolated Environment**: No conflicts with other AI/ML projects
- **Optimized Dependencies**: Exact versions tested for compatibility  
- **Professional UI**: Modern web interface for document analysis
- **Immediate Start**: Upload documents and start analyzing right away

**Ready to Use:**
- Upload legal documents (PDF, DOCX, TXT)
- Run AI analysis and summarization
- Generate legal database queries
- Search through your document collection

### 🔧 Advanced Options

```bash
# Recreate environment (if issues occur)
rag setup --force

# Activate existing environment 
rag setup --activate

# Custom server options
rag serve --port 3000 --host 0.0.0.0

# CLI document analysis (after setup)
rag analyze document.pdf

# Generate legal queries
rag query contract.pdf --database westlaw
```

### 🐍 Programmatic Usage

#### 1. Start the Web Interface
```bash
# Launch the web server
python -m lawfirm_rag.api.fastapi_app

# Open http://localhost:8000 in your browser
# Upload documents and start analyzing!
```

#### 2. Bulk Document Processing
```python
from lawfirm_rag.core.enhanced_document_processor import EnhancedDocumentProcessor

# Initialize processor
processor = EnhancedDocumentProcessor(
    temp_dir="./temp",
    chunk_size=1000,
    use_vector_db=True  # Enable vector search
)

# Create a collection
collection_id = processor.create_collection(
    name="Legal Cases 2024",
    description="Recent legal case documents"
)

# Process multiple files
results = processor.process_uploaded_files(file_objects, collection_id)
print(f"Processed {results['processed_documents']} documents")
```

#### 3. Vector Search
```python
from lawfirm_rag.core.vector_store import create_vector_store

# Create vector store
vector_store = create_vector_store("legal_docs", "legal")

# Add documents
doc_ids = vector_store.add_documents(
    texts=["Document text 1", "Document text 2"],
    metadatas=[{"type": "contract"}, {"type": "brief"}]
)

# Search documents
results = vector_store.search(
    query="contract disputes",
    n_results=10,
    filter_metadata={"type": "contract"}
)
```

#### 4. AI Analysis
```python
from lawfirm_rag.core.ai_engine import create_ai_engine_from_config
from lawfirm_rag.utils.config import ConfigManager

# Initialize AI engine
config = ConfigManager().get_config()
ai_engine = create_ai_engine_from_config(config)

if ai_engine.load_model():
    # Analyze document
    analysis = ai_engine.analyze_document(text, "summary")
    print(f"Summary: {analysis}")
    
    # Generate legal queries
    query = ai_engine.generate_legal_query(text, "westlaw")
    print(f"Westlaw Query: {query}")
```

## 🔧 System Requirements

### Required Dependencies
- **Python**: 3.11+ (recommended: 3.11 or 3.12)
- **Automatic Environment**: The `rag setup` command automatically creates an isolated environment with:
  - PyTorch 2.1.0+cpu (CPU-optimized version for maximum compatibility)
  - ChromaDB 0.4.15 (vector database) 
  - Sentence Transformers 4.1.0 (latest stable embeddings)
  - FastAPI + Uvicorn (web interface)
  - Rich CLI interface
  - All other dependencies with exact pinned versions

### Why Isolated Environment?
This package uses **specific versions** of AI/ML libraries that may conflict with other projects. The automatic environment setup ensures:
- ✅ **No Conflicts**: Won't break your other Python projects
- ✅ **Exact Versions**: Uses tested combinations of PyTorch + ChromaDB + transformers
- ✅ **Professional Setup**: Same approach used by Anaconda, Ollama, etc.
- ✅ **Easy Management**: Single command setup and activation

### Optional AI Backends
- **Ollama**: Easy local model management (recommended)
- **Local GGUF**: Direct model file loading
- **API Models**: OpenAI, Anthropic, etc. (via configuration)

## 🎉 Latest Release Highlights

### v2.0 - Production Ready Release
**Major breakthrough**: Complete end-to-end functionality achieved!

#### 🔧 **Critical Fixes Implemented**
- **PyTorch Compatibility**: Resolved PyTorch 2.1.0+cpu `get_default_device()` errors with compatibility shim
- **ChromaDB Integration**: Fixed schema conflicts with automatic database reset capability
- **Vector Store Unification**: Resolved dual document system - both text input and file uploads now searchable
- **Bulk Upload Pipeline**: Fixed field name mismatches and metadata validation for ChromaDB
- **JSON File Support**: Added structured text extraction for JSON documents

#### ⚡ **Performance & Reliability**
- **Environment Optimization**: Automatic configuration prevents PyTorch/OpenMP hanging issues
- **Error Recovery**: Comprehensive error handling with graceful fallback mechanisms
- **Memory Management**: Optimized for processing large document collections
- **Progress Tracking**: Real-time progress updates for bulk operations

#### 🔍 **Enhanced Search Capabilities**
- **Unified Vector Store**: Single search interface for all document types
- **384-Dimensional Embeddings**: High-quality semantic search with sentence-transformers
- **Metadata Sanitization**: Automatic conversion of complex metadata for database compatibility
- **Zero-Vector Fallback**: Handles empty documents gracefully

#### 🌟 **Production Features**
- **Batch Processing**: Handle 1000+ documents with progress tracking
- **Automatic Recovery**: Database schema mismatch detection and reset
- **Multi-Format Support**: Enhanced PDF, DOCX, TXT, and JSON processing
- **Enterprise Ready**: Comprehensive logging, monitoring, and error handling

This release represents a complete, working system ready for production use in legal document analysis workflows.

## Features

- 📄 **Document Processing**: Extract and analyze text from various legal document formats
- 🤖 **AI-Powered Analysis**: Support for both Ollama and local GGUF models for document summarization and legal issue identification
- 🔍 **Query Generation**: Generate optimized search queries for legal databases (Westlaw, LexisNexis, Casetext)
- 🌐 **Web Interface**: Modern web UI for document upload and analysis
- 🔧 **CLI Tools**: Command-line interface for batch processing
- 💾 **Model Management**: Download, load, and manage AI models with progress tracking
- 🏗️ **Pip Installable**: Clean package structure for easy installation and distribution
- 🚀 **Ollama Integration**: Easy setup with Ollama for improved installation experience

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama** (required for AI models):
   - Visit [ollama.ai](https://ollama.ai) and download for your OS
   - Start Ollama: `ollama serve`

2. **Install LawFirm-RAG**:
   ```bash
   pip install lawfirm-rag
   ```

### Setup Models

**Option 1: Quick Setup (Recommended)**
```python
from lawfirm_rag.utils.setup import quick_setup
quick_setup()  # Downloads essential models automatically
```

**Option 2: Manual Setup**
```bash
# Essential models for basic functionality
ollama pull llama3.2              # General chat model
ollama pull mxbai-embed-large     # Embeddings model

# Optional: Legal-specific model for enhanced legal analysis
ollama pull hf.co/TheBloke/law-chat-GGUF:Q4_0
```

**Option 3: Check Status and Get Instructions**
```python
from lawfirm_rag.utils.setup import print_setup_instructions
print_setup_instructions()  # Shows current status and setup commands
```

### Basic Usage

```python
from lawfirm_rag import AIEngine, DocumentProcessor

# Initialize the AI engine (auto-detects available models)
ai_engine = AIEngine()
ai_engine.load_model()

# Process a legal document
processor = DocumentProcessor()
text = processor.extract_text("path/to/legal_document.pdf")

# Analyze the document
summary = ai_engine.analyze_document(text, analysis_type="summary")
legal_issues = ai_engine.analyze_document(text, analysis_type="legal_issues")

# Generate search queries for legal databases
westlaw_query = ai_engine.generate_search_query(text, database="westlaw")
print(f"Westlaw Query: {westlaw_query}")
```

## AI Model Setup

The package supports multiple AI backends for flexibility and ease of use:

### Ollama Backend (Recommended)
- **Easy Installation**: No compilation required
- **Model Management**: Built-in model downloading and management
- **Better Performance**: Optimized for local inference
- **Setup**: Install Ollama and pull models as shown above

### Local GGUF Backend (Advanced)
- **Direct Model Loading**: Load GGUF files directly
- **Full Control**: Manual model management
- **Setup**: 
  1. Via Web Interface: Use the Model Management section to download models
  2. Manual Download: Place GGUF files in the `models/` directory
  3. Recommended Model: [Law Chat GGUF](https://huggingface.co/TheBloke/law-chat-GGUF) (Q4_0 variant)

### Backend Selection
The package automatically detects the best available backend:
1. **Ollama** (if server is running and models are available)
2. **Local GGUF** (if models are found in the models directory)
3. **Fallback** (graceful degradation with limited functionality)

You can force a specific backend by creating a `config.yaml` file:
```yaml
llm:
  backend: ollama  # or "llama-cpp" for GGUF files
  ollama:
    base_url: http://localhost:11434

# Model configuration for different use cases
models:
  chat: llama3.2                    # General conversation
  legal_analysis: law-chat          # Legal document analysis
  query_generation: llama3.2        # Search query generation
  embeddings: mxbai-embed-large     # Text embeddings
  fallback: llama3.2               # Fallback when primary models fail
```

## Architecture

```
lawfirm_rag/
├── core/           # Core processing modules
│   ├── ai_engine.py       # GGUF model handling
│   ├── document_processor.py  # Document text extraction
│   ├── query_generator.py     # Legal database query generation
│   └── storage.py            # Document storage layer
├── api/            # FastAPI web server
├── cli/            # Command-line interface
├── web/            # Frontend assets
└── utils/          # Utilities and configuration
```

## Legal Database Support

### Westlaw
- **Syntax**: Terms and Connectors
- **Operators**: `&`, `|`, `/s`, `/p`, `/n`, `!`, `%`
- **Example**: `negligen! /p \"motor vehicle\" /s injur! & damag!`

### LexisNexis
- **Syntax**: Boolean operators
- **Operators**: `AND`, `OR`, `NOT`, `W/n`, `PRE/n`
- **Example**: `negligence AND \"motor vehicle\" AND damages`

### Casetext
- **Syntax**: Natural language + Boolean
- **Features**: Supports both natural language and boolean queries

## Development

### Project Structure
This project uses Task Master for development workflow management:

```bash
# View current tasks
task-master list

# Get next task to work on
task-master next

# Mark task complete
task-master set-status --id=X --status=done
```

### Running Tests
```bash
# Install development dependencies
pip install -e \".[dev]\"

# Run tests
pytest

# Run with coverage
pytest --cov=lawfirm_rag
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Configuration

Configuration is managed through multiple methods:

### Configuration Files
- **`config.yaml`**: Main configuration file (project root)
- **`~/.lawfirm-rag/config.yaml`**: User-level configuration
- **`.env`**: Environment variables and API keys

### Model Configuration
The package uses a flexible model configuration system that allows you to specify different models for different purposes:

```yaml
# config.yaml
models:
  chat: llama3.2                    # General conversation and chat
  legal_analysis: law-chat          # Legal document analysis and summarization
  query_generation: llama3.2        # Search query generation for legal databases
  embeddings: mxbai-embed-large     # Text embeddings for semantic search
  fallback: llama3.2               # Fallback model when primary models fail
```

### LLM Backend Configuration
```yaml
# config.yaml
llm:
  backend: ollama  # "auto", "ollama", or "llama-cpp"
  ollama:
    base_url: http://localhost:11434
    timeout: 30
    max_retries: 3
  llama_cpp:
    model_path: ~/.lawfirm-rag/models/default.gguf
```

## API Reference

### FastAPI Endpoints

- `POST /upload` - Upload documents for analysis
- `POST /analyze` - Analyze uploaded documents
- `POST /query` - Generate database queries
- `GET /health` - Service health check
- `POST /models/load` - Load AI models
- `GET /models/loaded` - Get loaded model status

### Python API

```python
from lawfirm_rag.core import DocumentProcessor, AIEngine, QueryGenerator
from lawfirm_rag.core.ai_engine import create_ai_engine_from_config
from lawfirm_rag.utils.config import ConfigManager

# Initialize components with automatic backend detection
config_manager = ConfigManager()
config = config_manager.get_config()

processor = DocumentProcessor()
ai_engine = create_ai_engine_from_config(config)  # Auto-detects Ollama or GGUF
query_gen = QueryGenerator(ai_engine)

# Manual backend selection
ai_engine = AIEngine(backend_type="ollama", model_name="law-chat")
# or
ai_engine = AIEngine(backend_type="llama-cpp", model_path="path/to/model.gguf")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- Uses [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for local AI model support
- Task management powered by [Task Master AI](https://github.com/taskmaster-ai/taskmaster-ai)

## Support

For questions, issues, or contributions:
- 🐛 Issues: [GitHub Issues](https://github.com/DannyMExe/rag-package/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/DannyMExe/rag-package/discussions)

[project.urls]
Homepage = "https://github.com/DannyMExe/rag-package"
Documentation = "https://lawfirm-rag.readthedocs.io"
Repository = "https://github.com/DannyMExe/rag-package"
"Bug Tracker" = "https://github.com/DannyMExe/rag-package/issues"
Changelog = "https://github.com/DannyMExe/rag-package/blob/main/CHANGELOG.md" 