# LawFirm RAG Package

A comprehensive Python package for document analysis and query generation using Retrieval-Augmented Generation (RAG) with local AI models. Currently optimized for legal documents with support for Westlaw, LexisNexis, and Casetext query generation.

## Features

- 📄 **Document Processing**: Extract and analyze text from various legal document formats
- 🤖 **AI-Powered Analysis**: Support for both Ollama and local GGUF models for document summarization and legal issue identification
- 🔍 **Query Generation**: Generate optimized search queries for legal databases (Westlaw, LexisNexis, Casetext)
- 🌐 **Web Interface**: Modern web UI for document upload and analysis
- 🔧 **CLI Tools**: Command-line interface for batch processing
- 💾 **Model Management**: Download, load, and manage AI models with progress tracking
- 🏗️ **Pip Installable**: Clean package structure for easy installation and distribution
- 🚀 **Ollama Integration**: Easy setup with Ollama for improved installation experience

## Quick Start

### Installation

#### From PyPI (Recommended)
```bash
# Install the package (Ollama backend only)
pip install rag-package

# Or install with GGUF backend support (requires compilation)
pip install rag-package[gguf]
```

#### From GitHub Repository
```bash
# Clone the repository
git clone https://github.com/DannyMExe/rag-package.git
cd rag-package

# Install the package in development mode
pip install -e .
```

### AI Backend Setup

The package supports two AI backends:

#### Option 1: Ollama (Recommended - Easier Setup)
1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)
2. **Pull a model**: 
   ```bash
   # For legal documents (recommended)
   ollama run hf.co/TheBloke/law-chat-GGUF:Q4_0
   
   # Or use a general model
   ollama pull llama3.2
   ```
3. **Configure**: The package will auto-detect Ollama and use it by default

#### Option 2: Local GGUF Models (Advanced)
1. **Install GGUF support**: `pip install rag-package[gguf]` (requires compilation tools)
2. **Download models**: Place GGUF files in the `models/` directory
3. **Recommended**: [Law Chat GGUF](https://huggingface.co/TheBloke/law-chat-GGUF) (Q4_0 variant)
4. **Configure**: Set `backend: "llama-cpp"` in your config file

### Basic Usage

#### Web Interface
```bash
# Start the web server
rag serve

# Or using Python module
python -m uvicorn lawfirm_rag.api.fastapi_app:app --reload

# Open http://localhost:8000/app in your browser
```

#### CLI Usage
```bash
# Analyze documents
rag analyze document.pdf --type summary

# Generate queries for legal databases
rag query document.pdf --database westlaw

# Process multiple files
rag analyze *.pdf --output results.json

# Additional options
rag serve --port 8080
rag analyze document.pdf --type summary
```

### Git Bash Usage

If you're using Git Bash on Windows and the `rag` command isn't found, use one of these options:

#### Option 1: Use Python module syntax
```bash
# Run any command through the Python module
python -m lawfirm_rag.cli.main serve
python -m lawfirm_rag.cli.main analyze document.pdf
```

#### Option 2: Add Scripts directory to Git Bash PATH
Add this line to your `~/.bashrc` file:
```bash
# Adjust the Python version in the path if needed
export PATH="$PATH:/c/Users/$USERNAME/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/Scripts"
```
Then restart Git Bash or run `source ~/.bashrc`

#### Option 3: Create an alias
Add this line to your `~/.bashrc` file:
```bash
alias rag="python -m lawfirm_rag.cli.main"
```
Then restart Git Bash or run `source ~/.bashrc`

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
    default_model: law-chat
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

### LLM Backend Configuration
```yaml
# config.yaml
llm:
  backend: ollama  # "auto", "ollama", or "llama-cpp"
  ollama:
    base_url: http://localhost:11434
    default_model: law-chat
    default_embed_model: mxbai-embed-large
    timeout: 30
    max_retries: 3
  llama_cpp:
    model_path: ~/.lawfirm-rag/models/default.gguf
    n_ctx: 4096
    temperature: 0.7
```

### Environment Variables
```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Legacy GGUF Model Settings (if using llama-cpp backend)
LAWFIRM_RAG_CONFIG_PATH=./config.yaml

# Optional: API keys for cloud models (future feature)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
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