import json
import fitz  # PyMuPDF
from typing import Dict, Any
from bs4 import BeautifulSoup
import re

class DocumentProcessor:
    """Process various document types and extract text content"""
    
    def __init__(self):
        self.supported_types = {
            'text/plain': self._process_text,
            'text/markdown': self._process_text,
            'application/json': self._process_json,
            'text/html': self._process_html,
            'application/pdf': self._process_pdf
        }
    
    def process_document(self, content: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Process document and return structured data"""
        try:
            # Determine processor based on content type or file extension
            processor = self._get_processor(content_type, filename)
            
            # Process the document
            text_content = processor(content)
            
            # Chunk the content
            chunks = self._chunk_text(text_content, filename)
            
            return {
                'filename': filename,
                'content_type': content_type,
                'text_content': text_content,
                'chunks': chunks,
                'metadata': {
                    'source': filename,
                    'type': content_type,
                    'chunk_count': len(chunks)
                }
            }
        except Exception as e:
            raise Exception(f"Error processing {filename}: {str(e)}")
    
    def _get_processor(self, content_type: str, filename: str):
        """Determine appropriate processor"""
        if content_type in self.supported_types:
            return self.supported_types[content_type]
        
        # Fallback to file extension
        ext = filename.lower().split('.')[-1]
        if ext in ['txt', 'md']:
            return self._process_text
        elif ext == 'json':
            return self._process_json
        elif ext == 'html':
            return self._process_html
        elif ext == 'pdf':
            return self._process_pdf
        else:
            return self._process_text  # Default fallback
    
    def _process_text(self, content: bytes) -> str:
        """Process plain text or markdown files"""
        return content.decode('utf-8')
    
    def _process_json(self, content: bytes) -> str:
        """Process JSON files"""
        try:
            data = json.loads(content.decode('utf-8'))
            # Convert JSON to readable text format
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            return content.decode('utf-8')
    
    def _process_html(self, content: bytes) -> str:
        """Process HTML files"""
        try:
            # Use BeautifulSoup to extract text from HTML
            soup = BeautifulSoup(content.decode('utf-8'), 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            # Get text and clean it up
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text
        except:
            return content.decode('utf-8')
    
    def _process_pdf(self, content: bytes) -> str:
        """Process PDF files"""
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except:
            raise Exception("Failed to process PDF file")
    
    def _chunk_text(self, text: str, source: str, chunk_size: int = 1000, overlap: int = 200) -> list:
        """Split text into chunks for vector storage"""
        chunks = []
        
        # Simple chunking by character count with overlap
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundaries
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:
                    chunk = text[start:break_point + 1]
                    end = break_point + 1
            
            chunks.append({
                'text': chunk.strip(),
                'metadata': {
                    'source': source,
                    'chunk_index': len(chunks),
                    'start_char': start,
                    'end_char': end
                }
            })
            
            start = end - overlap
        
        return chunks