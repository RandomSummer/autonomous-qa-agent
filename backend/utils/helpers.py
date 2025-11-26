"""
Utility helper functions used across the application.
Common operations like file handling, text cleaning, ID generation.
"""

import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import uuid


def generate_chunk_id(text: str, index: int) -> str:
    """
    Generate a unique ID for a text chunk.
    Uses hash of text + index to ensure uniqueness.

    Args:
        text: The chunk text content
        index: Position in the document

    Returns:
        Unique identifier string
    """
    # Create hash from text content for uniqueness
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    return f"chunk_{index}_{text_hash}"


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    Removes extra whitespace, newlines, special characters.

    Args:
        text: Raw text string

    Returns:
        Cleaned text string
    """
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)

    # Remove special control characters
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.

    Args:
        filename: Name of the file

    Returns:
        Extension without dot (e.g., "md", "txt")
    """
    return Path(filename).suffix.lstrip('.').lower()


def format_file_size(size_bytes: int) -> str:
    """
    Convert bytes to human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string like "1.5 MB"
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def generate_test_id(index: int) -> str:
    """
    Generate standardized test case ID.

    Args:
        index: Sequential number of the test

    Returns:
        Formatted ID like "TC-001"
    """
    return f"TC-{index:03d}"


def generate_script_filename(test_id: str) -> str:
    """
    Generate filename for Selenium script.

    Args:
        test_id: Test case ID

    Returns:
        Filename like "test_TC-001.py"
    """
    return f"test_{test_id.replace('-', '_').lower()}.py"


def extract_code_from_markdown(text: str) -> str:
    """
    Extract code from markdown code blocks.
    Useful when LLM returns code wrapped in ```python ... ```

    Args:
        text: Text potentially containing markdown code blocks

    Returns:
        Extracted code or original text
    """
    # Pattern to match ```python or ``` code blocks
    pattern = r'```(?:python)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    if matches:
        # Return the first code block found
        return matches[0].strip()

    return text.strip()


def validate_html_content(html: str) -> bool:
    """
    Basic validation that content looks like HTML.

    Args:
        html: String to validate

    Returns:
        True if appears to be HTML
    """
    html_lower = html.lower().strip()
    return (
            '<html' in html_lower or
            '<!doctype html>' in html_lower or
            '<body' in html_lower
    )


def create_metadata_dict(
        source_document: str,
        chunk_index: int,
        total_chunks: int,
        **kwargs
) -> Dict[str, Any]:
    """
    Create standardized metadata dictionary for chunks.

    Args:
        source_document: Original document filename
        chunk_index: Position of this chunk
        total_chunks: Total number of chunks from document
        **kwargs: Additional metadata fields

    Returns:
        Metadata dictionary
    """
    metadata = {
        "source_document": source_document,
        "chunk_index": chunk_index,
        "total_chunks": total_chunks,
    }
    metadata.update(kwargs)
    return metadata


def safe_filename(filename: str) -> str:
    """
    Make filename safe by removing/replacing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Safe filename
    """
    # Remove/replace unsafe characters
    safe = re.sub(r'[^\w\s\-\.]', '_', filename)
    # Remove multiple underscores
    safe = re.sub(r'_+', '_', safe)
    return safe.strip('_')