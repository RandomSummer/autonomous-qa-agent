"""
Configuration management for the QA Agent system.
Loads environment variables and provides centralized settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Centralized configuration class.
    All paths and API keys are managed here for easy access.
    """

    # === API Keys ===
    # Groq API key for LLM inference - get from https://console.groq.com/
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # === Model Settings ===
    # LLM model to use - llama-3.3-70b is fast and high quality
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    # Embedding model for converting text to vectors
    # all-MiniLM-L6-v2 is lightweight, runs locally, good balance of speed/quality
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # === Directory Paths ===
    # Base project directory
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Where uploaded documents are stored temporarily
    UPLOAD_PATH: Path = BASE_DIR / "data" / "uploads"

    # Where ChromaDB stores vector embeddings
    VECTOR_DB_PATH: Path = BASE_DIR / "data" / "vector_db"

    # Where generated Selenium scripts are saved
    OUTPUT_PATH: Path = BASE_DIR / "data" / "outputs"

    # === Vector Database Settings ===
    # Name of the ChromaDB collection
    COLLECTION_NAME: str = "qa_knowledge_base"

    # === Text Chunking Settings ===
    # Size of each text chunk for embedding (in characters)
    # Smaller = more precise retrieval, Larger = more context
    CHUNK_SIZE: int = 1000

    # Overlap between chunks to maintain context continuity
    CHUNK_OVERLAP: int = 200

    # === RAG Settings ===
    # Number of similar chunks to retrieve for each query
    TOP_K_RESULTS: int = 5

    # === LLM Generation Settings ===
    # Maximum tokens for LLM response
    MAX_TOKENS: int = 2000

    # Temperature for LLM (0 = deterministic, 1 = creative)
    # Lower is better for code generation
    TEMPERATURE: float = 0.1

    @classmethod
    def create_directories(cls):
        """
        Create all necessary directories if they don't exist.
        Called on startup to ensure data folders are ready.
        """
        cls.UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        print("[OK] All directories verified/created")

    @classmethod
    def validate(cls):
        """
        Validate that required settings are present.
        Raises error if critical config is missing.
        """
        if not cls.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )
        print("[OK] Configuration validated")


# Create singleton instance
settings = Settings()