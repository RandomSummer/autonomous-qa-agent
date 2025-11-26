"""
FastAPI Backend for Autonomous QA Agent
Exposes all services through REST API endpoints.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
from pathlib import Path
import shutil
import sys
import io

# Force UTF-8 encoding for stdout/stderr on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from backend.config import settings
from backend.models import (
    HealthResponse,
    KnowledgeBaseStatus,
    TestCaseRequest,
    TestCaseResponse,
    ScriptGenerationRequest,
    ScriptGenerationResponse,
    UploadResponse
)
from backend.services.document_parser import document_parser
from backend.services.vector_store import vector_store
from backend.services.test_case_agent import test_case_agent
from backend.services.script_agent import script_agent

# Initialize FastAPI app
app = FastAPI(
    title="Autonomous QA Agent API",
    description="AI-powered test case and Selenium script generation",
    version="1.0.0"
)

# Add CORS middleware for Streamlit frontend
# Why? Allows Streamlit (different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Verifies API is running and checks configuration status.
    
    Returns:
        HealthResponse with status and configuration info
    """
    stats = vector_store.get_stats()
    
    return HealthResponse(
        status="healthy",
        groq_api_configured=bool(settings.GROQ_API_KEY),
        vector_db_initialized=stats['total_chunks'] > 0
    )


# ============================================================================
# FILE UPLOAD ENDPOINTS
# ============================================================================

@app.post("/api/upload/documents", response_model=List[UploadResponse])
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload multiple support documents (MD, TXT, JSON, PDF, HTML).
    Files are saved to upload directory for processing.
    
    Args:
        files: List of files to upload
    
    Returns:
        List of UploadResponse for each file
    
    Example:
        POST /api/upload/documents
        files: [product_specs.md, ui_guide.txt]
    """
    responses = []
    
    for file in files:
        try:
            # Save file to upload directory
            file_path = settings.UPLOAD_PATH / file.filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            responses.append(UploadResponse(
                success=True,
                message=f"File uploaded successfully",
                filename=file.filename,
                file_path=str(file_path)
            ))
            
        except Exception as e:
            responses.append(UploadResponse(
                success=False,
                message=f"Upload failed: {str(e)}",
                filename=file.filename,
                file_path=""
            ))
    
    return responses


@app.post("/api/upload/html")
async def upload_html(file: UploadFile = File(...)):
    """
    Upload HTML file (checkout.html).
    Stored separately for easy access during script generation.
    
    Args:
        file: HTML file to upload
    
    Returns:
        UploadResponse with file details
    """
    try:
        file_path = settings.UPLOAD_PATH / "checkout.html"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return UploadResponse(
            success=True,
            message="HTML file uploaded successfully",
            filename=file.filename,
            file_path=str(file_path)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# KNOWLEDGE BASE ENDPOINTS
# ============================================================================

@app.post("/api/knowledge-base/build", response_model=KnowledgeBaseStatus)
async def build_knowledge_base(clear_existing: bool = False):
    """
    Build knowledge base from uploaded documents.
    
    Process:
    1. Clear existing vector DB (if requested)
    2. Parse all files in upload directory
    3. Generate embeddings
    4. Store in ChromaDB
    
    Args:
        clear_existing: Whether to clear existing data first
    
    Returns:
        KnowledgeBaseStatus with build results
    
    Example:
        POST /api/knowledge-base/build?clear_existing=true
    """
    try:
        # Clear if requested
        if clear_existing:
            vector_store.clear_collection()
            print("[CLEAR] Cleared existing knowledge base")
        
        # Get all files from upload directory
        upload_files = list(settings.UPLOAD_PATH.glob("*"))
        
        # Exclude .gitkeep and system files
        upload_files = [
            f for f in upload_files 
            if f.is_file() and not f.name.startswith('.')
        ]
        
        if not upload_files:
            return KnowledgeBaseStatus(
                success=False,
                message="No documents found in upload directory",
                total_documents=0,
                total_chunks=0
            )
        
        print(f"\n[BUILD] Building knowledge base from {len(upload_files)} files...")
        
        # Parse documents
        parse_results = document_parser.parse_multiple_files(upload_files)
        successful_docs = [doc for doc in parse_results['documents'] if doc['success']]
        
        if not successful_docs:
            return KnowledgeBaseStatus(
                success=False,
                message="Failed to parse any documents",
                total_documents=0,
                total_chunks=0
            )
        
        # Add to vector store
        vector_result = vector_store.add_documents(successful_docs)
        
        if vector_result['success']:
            doc_names = [doc['metadata']['filename'] for doc in successful_docs]
            
            return KnowledgeBaseStatus(
                success=True,
                message="Knowledge base built successfully",
                total_documents=vector_result['total_documents'],
                total_chunks=vector_result['total_chunks'],
                documents_processed=doc_names
            )
        else:
            raise Exception(vector_result['message'])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-base/stats")
async def get_knowledge_base_stats():
    """
    Get statistics about the knowledge base.
    
    Returns:
        Dict with total_chunks, total_documents, documents list
    """
    return vector_store.get_stats()


# ============================================================================
# TEST CASE GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/test-cases/generate", response_model=TestCaseResponse)
async def generate_test_cases(request: TestCaseRequest):
    """
    Generate test cases based on user query.
    Uses RAG to retrieve relevant docs and LLM to generate cases.
    
    Args:
        request: TestCaseRequest with query and options
    
    Returns:
        TestCaseResponse with generated test cases
    
    Example:
        POST /api/test-cases/generate
        {
            "query": "Generate test cases for discount code feature",
            "include_negative": true
        }
    """
    try:
        print(f"\n[TEST] Generating test cases for: {request.query}")
        
        response = test_case_agent.generate_test_cases(
            user_query=request.query,
            include_negative=request.include_negative
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SELENIUM SCRIPT GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/scripts/generate", response_model=ScriptGenerationResponse)
async def generate_selenium_script(request: ScriptGenerationRequest):
    """
    Generate Selenium Python script from a test case.
    
    Process:
    1. Receive test case + HTML content
    2. Extract HTML elements
    3. Use RAG to get additional context
    4. Generate Python Selenium script
    5. Save to outputs directory
    
    Args:
        request: ScriptGenerationRequest with test_case and html_content
    
    Returns:
        ScriptGenerationResponse with generated script
    
    Example:
        POST /api/scripts/generate
        {
            "test_case": {...},
            "html_content": "<html>...</html>"
        }
    """
    try:
        print(f"\n[SCRIPT] Generating script for: {request.test_case.test_id}")
        
        response = script_agent.generate_script(
            test_case=request.test_case,
            html_content=request.html_content
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scripts/download/{filename}")
async def download_script(filename: str):
    """
    Download a generated Selenium script.
    
    Args:
        filename: Name of script file to download
    
    Returns:
        File download response
    
    Example:
        GET /api/scripts/download/test_tc_001.py
    """
    file_path = settings.OUTPUT_PATH / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Script not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/x-python"
    )


@app.get("/api/scripts/list")
async def list_generated_scripts():
    """
    List all generated Selenium scripts.
    
    Returns:
        Dict with list of script filenames
    """
    scripts = list(settings.OUTPUT_PATH.glob("*.py"))
    script_names = [s.name for s in scripts]
    
    return {
        "total": len(script_names),
        "scripts": script_names
    }


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.delete("/api/uploads/clear")
async def clear_uploads():
    """
    Clear all uploaded files.
    Useful for starting fresh.
    
    Returns:
        Success message
    """
    try:
        for file in settings.UPLOAD_PATH.glob("*"):
            if file.is_file() and not file.name.startswith('.'):
                file.unlink()
        
        return {"message": "All uploads cleared successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/uploads/list")
async def list_uploads():
    """
    List all uploaded files.
    
    Returns:
        Dict with list of uploaded filenames
    """
    files = [
        f.name for f in settings.UPLOAD_PATH.glob("*") 
        if f.is_file() and not f.name.startswith('.')
    ]
    
    return {
        "total": len(files),
        "files": files
    }


# Run server with: uvicorn backend.main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)