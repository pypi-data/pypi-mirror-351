# RAG Package

A comprehensive Python package for document analysis and query generation using Retrieval-Augmented Generation (RAG) with local AI models. Currently optimized for legal documents with support for Westlaw, LexisNexis, and Casetext query generation.

## Features

- 📄 **Document Processing**: Extract and analyze text from various legal document formats
- 🤖 **AI-Powered Analysis**: Local GGUF model support for document summarization and legal issue identification
- 🔍 **Query Generation**: Generate optimized search queries for legal databases (Westlaw, LexisNexis, Casetext)
- 🌐 **Web Interface**: Modern web UI for document upload and analysis
- 🔧 **CLI Tools**: Command-line interface for batch processing
- 💾 **Model Management**: Download, load, and manage AI models with progress tracking
- 🏗️ **Pip Installable**: Clean package structure for easy installation and distribution

## Quick Start

### Installation

#### From GitHub Repository
```bash
# Clone the repository
git clone https://github.com/DannyMExe/rag-package.git
cd rag-package

# Install the package
pip install -e .
```

#### From PyPI
```bash
# Install directly from PyPI
pip install lawfirm-rag-package
```

### Basic Usage

#### Web Interface
```bash
# Start the web server (simplest)
lrag serve

# Or use the full command name
lawfirm-rag serve

# Open http://localhost:8000/app in your browser
```

#### CLI Usage
```bash
# Start web server (simplest)
lrag serve

# Analyze documents
lrag analyze document.pdf --type summary

# Generate queries  
lrag query document.pdf --database westlaw

# Process multiple files
lrag analyze *.pdf --output results.json

# Full command examples
lawfirm-rag serve --port 8080
lawfirm-rag analyze document.pdf --type summary
```

## AI Model Setup

The package supports local GGUF models for privacy and offline operation:

1. **Via Web Interface**: Use the Model Management section to download models
2. **Manual Download**: Place GGUF files in the `models/` directory
3. **Recommended Model**: [Law Chat GGUF](https://huggingface.co/TheBloke/law-chat-GGUF) (Q4_0 variant recommended)

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

Configuration is managed through:
- **`.taskmasterconfig`**: AI model settings and parameters
- **`.env`**: API keys and sensitive configuration (see `.env.example`)

### Environment Variables
```bash
# AI Provider API Keys (optional - for cloud models)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here

# Local model settings
OLLAMA_BASE_URL=http://localhost:11434/api
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

# Initialize components
processor = DocumentProcessor()
ai_engine = AIEngine(\"path/to/model.gguf\")
query_gen = QueryGenerator(ai_engine)

# Process document
text = processor.extract_text(\"document.pdf\")
summary = ai_engine.analyze_document(text, \"summary\")
query = query_gen.generate_query(text, \"westlaw\")
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