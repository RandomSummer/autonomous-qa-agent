# Autonomous QA Agent for Test Case and Script Generation

A production-ready QA automation system that transforms project documentation into comprehensive test suites. The agent intelligently processes support documents to generate grounded test cases and executable Selenium scripts, eliminating manual test writing while ensuring complete coverage based on actual requirements.

## Core Capabilities

- **Multi-format Document Processing** - Supports Markdown, TXT, JSON, and PDF files
- **Vector-based Knowledge Retrieval** - ChromaDB-powered semantic search for accurate context retrieval
- **Grounded Test Generation** - AI-powered test case creation strictly based on provided documentation
- **Executable Script Generation** - Converts test cases to production-ready Selenium Python scripts
- **RESTful API Backend** - FastAPI-based service architecture with comprehensive documentation
- **Interactive Web Interface** - Streamlit-powered UI for seamless workflow management

## How It Works

The QA Agent follows a streamlined workflow to transform your documentation into automated tests:

![Workflow Diagram](autonomous-qa-agent-architecture.png)

The system processes documents through five key stages:
1. **Document Upload** - Multi-format file ingestion and parsing
2. **Knowledge Base Creation** - Vector embeddings and semantic indexing
3. **AI-Powered Query Processing** - Gemini 2.5 analyzes requirements
4. **Test Case Generation** - Structured test scenarios with documentation references
5. **Script Generation** - Production-ready Selenium automation code

## Requirements

- **Python 3.8+**
- All dependencies are listed in `requirements.txt`

## Quick Start

1. **Navigate to project directory**
```bash
cd qa-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python start_app.py
```

4. **Open your browser** to http://localhost:8501

*Note: Required AI models will download automatically on first use.*

## Running the Application

```bash
python start_app.py
```

This single command starts both the FastAPI backend and Streamlit frontend automatically.

### Access the Application
- **Main Interface**: http://localhost:8501 (Streamlit UI)
- **API Documentation**: http://localhost:8000/docs (FastAPI docs)/docs

## Usage Workflow

### Document Ingestion
Upload support documents including specifications, UI guidelines, API documentation, and business requirements. The system accepts multiple formats and processes them into a searchable knowledge base.

### Knowledge Base Construction
The system chunks documents, generates semantic embeddings, and stores them in a vector database for intelligent retrieval during test generation.

### Test Case Generation
Query the system with natural language requests such as "Generate test cases for form validation" or "Create tests for payment processing workflow". The agent retrieves relevant documentation context and generates comprehensive test scenarios.

The system uses advanced AI models when available for higher-fidelity test generation, with automatic fallback to rule-based generation ensuring the system works reliably in all environments.

### Script Generation
Select generated test cases to convert into executable Selenium Python scripts. The system uses **Gemini AI** to analyze your HTML structure, project requirements, and test case context to generate intelligent, context-aware scripts with accurate element selectors, proper assertions, and robust error handling.

### Execution and Integration
Generated scripts are ready for immediate execution or integration into existing CI/CD pipelines and test automation frameworks.

## Project Structure

```
qa-agent/
├── backend/
│   ├── main.py                    # FastAPI application
│   └── services/                  # Core business logic
│       ├── document_processor.py  # Document processing
│       ├── knowledge_base.py      # Vector database management
│       ├── test_generator.py      # Test case generation
│       └── script_generator.py    # Selenium script generation
├── frontend/
│   └── app.py                     # Streamlit interface
├── assets/
│   ├── checkout.html              # Target web application
│   └── support_docs/              # Sample support documents
├── tests/
│   ├── generated_scripts/         # Generated Selenium scripts
│   └── sample_generated_script.py # Example output
├── requirements.txt               # Python dependencies
├── start_app.py                   # Application launcher
└── README.md                      # This file
```

## Sample Implementation

### Target Web Application
The repository includes a complete e-commerce checkout implementation (`checkout.html`) featuring:
- Product catalog with cart management
- Form validation and error handling
- Payment processing workflow
- Responsive design patterns

### Documentation Suite
Five comprehensive support documents demonstrate real-world usage:

| Document | Purpose | Content |
|----------|---------|---------|
| `product_specs.md` | Feature Specifications | Business rules, discount logic, shipping calculations |
| `ui_ux_guide.txt` | Interface Guidelines | Validation rules, error messaging, accessibility requirements |
| `api_endpoints.json` | Technical Specifications | REST API contracts, request/response schemas |
| `business_requirements.md` | Functional Requirements | User stories, acceptance criteria, business logic |
| `test_scenarios.md` | Quality Assurance | Edge cases, boundary conditions, regression scenarios |

## Technical Implementation

### Backend Services
- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **ChromaDB Integration**: Vector database for semantic document retrieval
- **Sentence Transformers**: State-of-the-art embedding models for text encoding
- **Modular Architecture**: Separated concerns for document processing, knowledge management, and generation

### Frontend Interface  
- **Streamlit Framework**: Interactive web interface with real-time feedback
- **File Upload Handling**: Multi-format document processing with progress indicators
- **Code Display**: Syntax-highlighted script output with copy functionality
- **Responsive Design**: Cross-platform compatibility and mobile support

### Data Processing
- **Document Parsing**: Intelligent text extraction preserving structure and metadata
- **Chunking Strategy**: Context-aware segmentation optimized for retrieval accuracy
- **Embedding Generation**: Transformer-based vector representations for semantic search
- **Metadata Management**: Source tracking and provenance for generated content

## Configuration and Deployment

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for large document sets)
- Internet connection for initial model downloads
- Available ports 8000 (FastAPI) and 8501 (Streamlit)

### Environment Configuration
The application automatically manages dependencies and model downloads. For production deployments, consider:
- Containerization with Docker for consistent environments
- Reverse proxy configuration for external access
- Resource allocation for vector database operations
- Persistent storage for knowledge base data

### Performance Optimization
- **Document Size**: Limit individual documents to 10MB for optimal processing
- **Query Specificity**: Use precise, domain-specific queries for better retrieval accuracy
- **Knowledge Base Management**: Rebuild knowledge base when switching project contexts
- **Concurrent Usage**: FastAPI backend supports multiple simultaneous requests

### Troubleshooting

| Issue | Diagnosis | Resolution |
|-------|-----------|------------|
| Startup Failure | Port conflicts or missing dependencies | Verify port availability, reinstall requirements |
| Model Download Issues | Network connectivity problems | Ensure stable internet connection, check firewall settings |
| Script Generation Errors | HTML structure mismatch | Validate target HTML against generated selectors |
| Performance Degradation | Large document processing | Optimize document chunking, consider hardware scaling |

## Architecture Overview

The system implements a Retrieval-Augmented Generation (RAG) architecture to ensure test generation is grounded in actual project documentation:

### Document Processing Pipeline
- **Text Extraction**: Multi-format document parsing with metadata preservation
- **Semantic Chunking**: Intelligent text segmentation maintaining context boundaries
- **Vector Embedding**: Transformer-based encoding for semantic similarity search
- **Storage Layer**: ChromaDB vector database with efficient retrieval mechanisms

### Test Generation Engine
- **Context Retrieval**: Semantic search across document embeddings
- **Prompt Engineering**: Structured prompts ensuring grounded generation
- **LLM Integration**: Large language model inference with retrieval context
- **Output Validation**: Generated content verification against source documentation

### Script Generation System
- **AI-Powered Generation**: Gemini 2.5 analyzes test cases, HTML structure, and project context
- **Intelligent Selector Strategy**: AI chooses optimal selectors based on reliability and maintainability
- **Context-Aware Logic**: Scripts generated based on actual project requirements and documentation
- **Robust Error Handling**: AI includes comprehensive exception handling and validation
- **Fallback Templates**: Rule-based generation ensures reliability when AI is unavailable

## Key Advantages

### Documentation Fidelity
All generated test cases include explicit references to source documentation, eliminating hallucinated features and ensuring alignment with actual requirements.

### AI-Powered Intelligence
**Gemini 2.5** analyzes your project context, HTML structure, and requirements to generate intelligent, context-aware Selenium scripts that understand your specific business logic and validation needs.

### Comprehensive Test Coverage
The system generates both positive and negative test scenarios, edge cases, and boundary conditions based on documented specifications.

### AI-Enhanced Production-Ready Output
Generated Selenium scripts leverage Gemini AI to include intelligent test logic, context-aware assertions, proper error handling, explicit waits, and maintainable code structure tailored to your specific project requirements and documentation.

### Scalable Architecture
Modular design supports integration with existing development workflows and scales to handle large documentation sets and complex web applications.
## Contributing

We welcome contributions from the community. Please follow these guidelines:

### Development Setup
1. Fork the repository and create a feature branch
2. Install development dependencies: `pip install -r requirements.txt`
3. Run tests to ensure baseline functionality
4. Make your changes with appropriate test coverage

### Code Standards
- Follow PEP 8 style guidelines
- Include docstrings for all public functions
- Add type hints where appropriate
- Maintain test coverage above 80%

### Pull Request Process
1. Update documentation for any new features
2. Add tests for new functionality
3. Ensure all existing tests pass
4. Update the README if needed
5. Submit PR with clear description of changes

### Issue Reporting
When reporting bugs, please include:
- Python version and operating system
- Complete error messages and stack traces
- Steps to reproduce the issue
- Sample documents if relevant

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [Streamlit](https://streamlit.io/)
- Powered by [ChromaDB](https://www.trychroma.com/) for vector storage
- Uses [Sentence Transformers](https://www.sbert.net/) for text embeddings
- Selenium integration for web automation testing

## Citation

If you use this project in your research or development, please cite:

```bibtex
@software{autonomous_qa_agent,
  title={Autonomous QA Agent for Test Case and Script Generation},
  author={Sk Sofiquee Fiaz},
  year={2025},
  url={https://github.com/RandomSummer/autonomous-qa-agent.git}
}
```
