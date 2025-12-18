from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os

import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.document_processor import DocumentProcessor
from services.knowledge_base import KnowledgeBase
from services.test_generator import TestGenerator
from services.script_generator import ScriptGenerator
from services.llm_client import GeminiClient

load_dotenv()

app = FastAPI(title="QA Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
doc_processor = DocumentProcessor()
knowledge_base = KnowledgeBase()
llm_client = GeminiClient()
test_generator = TestGenerator(knowledge_base, llm_client=llm_client)
script_generator = ScriptGenerator(knowledge_base, llm_client=llm_client)

class TestCaseRequest(BaseModel):
    query: str
    
class ScriptGenerationRequest(BaseModel):
    test_case: dict
    html_content: str

@app.post("/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process support documents"""
    try:
        processed_docs = []
        for file in files:
            content = await file.read()
            processed_doc = doc_processor.process_document(
                content, file.filename, file.content_type
            )
            processed_docs.append(processed_doc)
        
        return {"message": f"Processed {len(processed_docs)} documents", "documents": processed_docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/build-knowledge-base")
async def build_knowledge_base(documents: List[dict]):
    """Build vector database from processed documents"""
    try:
        knowledge_base.build_from_documents(documents)
        return {"message": "Knowledge base built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-test-cases")
async def generate_test_cases(request: TestCaseRequest):
    """Generate test cases based on query and knowledge base"""
    try:
        test_cases = test_generator.generate_test_cases(request.query)
        return {"test_cases": test_cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-script")
async def generate_script(request: ScriptGenerationRequest):
    """Generate Selenium script from test case"""
    try:
        script = script_generator.generate_selenium_script(
            request.test_case, request.html_content
        )
        return {"script": script}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)