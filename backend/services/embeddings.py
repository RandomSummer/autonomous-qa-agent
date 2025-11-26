"""
Embeddings Service
Generates vector embeddings from text using sentence-transformers.
Why sentence-transformers? Free, local, good quality, no API costs.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
from backend.config import settings


class EmbeddingService:
    """
    Handles text-to-vector conversion using sentence-transformers.
    Lazy loads model on first use to save memory.
    """

    def __init__(self):
        """Initialize without loading model (lazy loading)."""
        self._model = None
        self.model_name = settings.EMBEDDING_MODEL

    @property
    def model(self) -> SentenceTransformer:
        """
        Lazy load the embedding model.
        Only loads when first needed to save startup time.
        """
        if self._model is None:
            print(f"[INIT] Loading embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            print("[OK] Embedding model loaded")
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """
        Convert single text to embedding vector.

        Why normalize? Makes similarity search more accurate.

        Args:
            text: Text string to embed

        Returns:
            Vector embedding as list of floats

        Example:
            embedding = service.embed_text("This is a test")
            print(len(embedding))  # 384 dimensions for all-MiniLM-L6-v2
        """
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Convert multiple texts to embeddings efficiently.

        Why batch? Much faster than encoding one-by-one.
        batch_size=32 balances speed and memory usage.

        Args:
            texts: List of text strings
            batch_size: Number of texts to process at once

        Returns:
            List of embedding vectors

        Example:
            texts = ["text 1", "text 2", "text 3"]
            embeddings = service.embed_batch(texts)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return [emb.tolist() for emb in embeddings]

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embedding vectors.

        Returns:
            Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        return self.model.get_sentence_embedding_dimension()


# Singleton instance
embedding_service = EmbeddingService()