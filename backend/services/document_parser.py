"""
Document Parser Service
Extracts text content from various file formats: MD, TXT, JSON, HTML, PDF
Each parser handles format-specific extraction logic.
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
from bs4 import BeautifulSoup

# PyMuPDF for PDF parsing - handle both old and new versions
try:
    import fitz  # PyMuPDF < 1.24 (old versions had 'fitz' module)
except ImportError:
    try:
        import pymupdf as fitz  # PyMuPDF >= 1.24 (new versions use 'pymupdf')
    except ImportError:
        # If neither works, provide helpful error
        raise ImportError(
            "PyMuPDF is not installed. Install it with: pip install PyMuPDF"
        )

from backend.utils.helpers import clean_text, get_file_extension
from backend.models import DocumentMetadata


class DocumentParser:
    """
    Main parser class that routes files to appropriate handlers.
    Supports: .md, .txt, .json, .html, .pdf
    """

    def __init__(self):
        """Initialize parser with supported file extensions."""
        # Map extensions to parsing methods
        self.parsers = {
            'md': self._parse_markdown,
            'txt': self._parse_text,
            'json': self._parse_json,
            'html': self._parse_html,
            'htm': self._parse_html,
            'pdf': self._parse_pdf,
        }

    def parse_file(self, file_path: Path) -> Dict[str, any]:
        """
        Parse a file and extract its content.

        Args:
            file_path: Path to the file to parse

        Returns:
            Dictionary with:
                - content: Extracted text
                - metadata: File information
                - success: Whether parsing succeeded

        Example:
            result = parser.parse_file(Path("docs/spec.md"))
            print(result['content'])
        """
        try:
            # Get file extension to determine parser
            extension = get_file_extension(file_path.name)

            # Check if we support this file type
            if extension not in self.parsers:
                return {
                    'success': False,
                    'error': f"Unsupported file type: .{extension}",
                    'content': None,
                    'metadata': None
                }

            # Read file content
            file_stats = file_path.stat()

            # Route to appropriate parser
            parser_func = self.parsers[extension]
            content = parser_func(file_path)

            # Create metadata
            metadata = DocumentMetadata(
                filename=file_path.name,
                file_type=extension,
                size_bytes=file_stats.st_size
            )

            return {
                'success': True,
                'content': content,
                'metadata': metadata.dict(),
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': None,
                'metadata': None
            }

    def _parse_markdown(self, file_path: Path) -> str:
        """
        Parse Markdown files.
        Reads raw content - markdown formatting is useful context for LLM.

        Why keep markdown syntax?
        - Headers show document structure
        - Lists/bullets indicate relationships
        - Code blocks are already marked

        Args:
            file_path: Path to .md file

        Returns:
            Cleaned markdown text
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Clean but preserve markdown structure
        return clean_text(content)

    def _parse_text(self, file_path: Path) -> str:
        """
        Parse plain text files.
        Simple read and clean.

        Args:
            file_path: Path to .txt file

        Returns:
            Cleaned text content
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return clean_text(content)

    def _parse_json(self, file_path: Path) -> str:
        """
        Parse JSON files.
        Converts JSON to readable text format for LLM understanding.

        Why convert to text?
        - Embeddings work better on natural text
        - LLM can understand JSON structure in text form
        - Preserves key-value relationships

        Example:
            {"name": "test", "value": 123}
            becomes:
            "name: test\\nvalue: 123"

        Args:
            file_path: Path to .json file

        Returns:
            Text representation of JSON
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert JSON to readable text format
        return self._json_to_text(data)

    def _json_to_text(self, data: any, indent: int = 0) -> str:
        """
        Recursively convert JSON to readable text.
        Handles nested objects and arrays.

        Args:
            data: JSON data (dict, list, or primitive)
            indent: Current indentation level

        Returns:
            Formatted text string
        """
        lines = []
        prefix = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(self._json_to_text(value, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {value}")

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    lines.append(self._json_to_text(item, indent))
                else:
                    lines.append(f"{prefix}- {item}")

        else:
            lines.append(f"{prefix}{data}")

        return "\\n".join(lines)

    def _parse_html(self, file_path: Path) -> str:
        """
        Parse HTML files.
        Extracts text AND structure information.

        Why keep structure?
        - Form fields need IDs/names for Selenium
        - Button labels are important
        - Input types matter (text, email, radio, etc.)

        Strategy:
        - Extract visible text
        - Preserve important attributes (id, name, class, type)
        - Keep form structure for test generation

        Args:
            file_path: Path to .html file

        Returns:
            Text content with structural context
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'lxml')

        # Extract text with context
        text_parts = []

        # Get title
        if soup.title:
            text_parts.append(f"Page Title: {soup.title.string}")

        # Extract forms (important for testing)
        for form in soup.find_all('form'):
            text_parts.append("\\n--- Form ---")
            form_id = form.get('id', 'unnamed')
            text_parts.append(f"Form ID: {form_id}")

            # Extract inputs
            for inp in form.find_all(['input', 'textarea', 'select']):
                input_info = self._extract_input_info(inp)
                text_parts.append(input_info)

            # Extract buttons
            for btn in form.find_all(['button', 'input']):
                if btn.get('type') in ['submit', 'button'] or btn.name == 'button':
                    btn_text = btn.get_text(strip=True) or btn.get('value', '')
                    btn_id = btn.get('id', '')
                    text_parts.append(f"Button: {btn_text} (id: {btn_id})")

        # Get all visible text (fallback for non-form content)
        body_text = soup.get_text(separator=' ', strip=True)
        text_parts.append("\\n--- Page Content ---")
        text_parts.append(body_text)

        full_text = "\\n".join(text_parts)
        return clean_text(full_text)

    def _extract_input_info(self, element) -> str:
        """
        Extract detailed info from form inputs.
        Used by HTML parser to capture element details.

        Args:
            element: BeautifulSoup element (input/textarea/select)

        Returns:
            Formatted string with element details
        """
        tag = element.name
        input_type = element.get('type', 'text')
        input_id = element.get('id', '')
        input_name = element.get('name', '')
        input_placeholder = element.get('placeholder', '')

        info = f"Input: {tag}"
        if input_type != 'text':
            info += f" (type: {input_type})"
        if input_id:
            info += f" id='{input_id}'"
        if input_name:
            info += f" name='{input_name}'"
        if input_placeholder:
            info += f" placeholder='{input_placeholder}'"

        return info

    def _parse_pdf(self, file_path: Path) -> str:
        """
        Parse PDF files using PyMuPDF.
        Extracts text from all pages.

        Why PyMuPDF?
        - Fast and reliable
        - Handles most PDF formats
        - Preserves text structure better than alternatives

        Args:
            file_path: Path to .pdf file

        Returns:
            Extracted text from all pages
        """
        doc = fitz.open(file_path)
        text_parts = []

        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            if text.strip():
                text_parts.append(f"--- Page {page_num + 1} ---")
                text_parts.append(text)

        doc.close()

        full_text = "\\n".join(text_parts)
        return clean_text(full_text)

    def parse_multiple_files(self, file_paths: List[Path]) -> Dict[str, any]:
        """
        Parse multiple files at once.
        Useful for batch processing all uploaded documents.

        Args:
            file_paths: List of file paths to parse

        Returns:
            Dictionary with:
                - documents: List of parsed documents
                - total: Total files processed
                - successful: Number of successful parses
                - failed: Number of failed parses

        Example:
            files = [Path("doc1.md"), Path("doc2.pdf")]
            result = parser.parse_multiple_files(files)
            for doc in result['documents']:
                print(doc['content'])
        """
        documents = []
        successful = 0
        failed = 0

        for file_path in file_paths:
            result = self.parse_file(file_path)
            documents.append(result)

            if result['success']:
                successful += 1
            else:
                failed += 1

        return {
            'documents': documents,
            'total': len(file_paths),
            'successful': successful,
            'failed': failed
        }


# Create singleton instance for use across the app
document_parser = DocumentParser()