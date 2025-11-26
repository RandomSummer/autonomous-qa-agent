"""
Vector Store Service using ChromaDB
Stores document chunks with embeddings for semantic search (RAG).
Why ChromaDB? Lightweight, embedded, no server needed, perfect for this use case.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import settings
from backend.services.embeddings import embedding_service
from backend.utils.helpers import generate_chunk_id, create_metadata_dict


class VectorStore:
    """
    Manages document chunks in ChromaDB.
    Handles: chunking, embedding, storage, retrieval.
    """

    def __init__(self):
        """
        Initialize ChromaDB client and collection.
        Uses persistent storage so data survives restarts.
        """
        # Create ChromaDB client with persistent storage
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=str(settings.VECTOR_DB_PATH),
            anonymized_telemetry=False  # Disable telemetry
        ))

        # Get or create collection
        # Why "cosine"? Best for normalized embeddings (semantic similarity)
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}  # Cosine similarity for search
        )

        # Text splitter for chunking documents
        # Why RecursiveCharacterTextSplitter? Tries to keep semantic units together
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]  # Split by paragraphs first, then sentences
        )

        print(f"[OK] Vector store initialized: {settings.COLLECTION_NAME}")

    def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process and store multiple documents in vector DB.

        Process:
        1. Split each document into chunks
        2. Generate embeddings for chunks
        3. Store in ChromaDB with metadata

        Args:
            documents: List of dicts with 'content' and 'metadata'

        Returns:
            Stats: total_chunks, total_documents

        Example:
            docs = [
                {'content': 'text...', 'metadata': {'filename': 'doc.md'}},
                {'content': 'more...', 'metadata': {'filename': 'spec.txt'}}
            ]
            result = vector_store.add_documents(docs)
        """
        all_chunks = []
        all_embeddings = []
        all_metadatas = []
        all_ids = []

        total_chunks = 0

        for doc in documents:
            if not doc.get('content'):
                continue

            content = doc['content']
            doc_metadata = doc.get('metadata', {})
            filename = doc_metadata.get('filename', 'unknown')

            # Split document into chunks
            chunks = self.text_splitter.split_text(content)

            print(f"  [DOC] {filename}: {len(chunks)} chunks")

            # Prepare chunks for storage
            for i, chunk in enumerate(chunks):
                chunk_id = generate_chunk_id(chunk, i)

                # Create metadata with source tracking
                metadata = create_metadata_dict(
                    source_document=filename,
                    chunk_index=i,
                    total_chunks=len(chunks),
                    file_type=doc_metadata.get('file_type', ''),
                    file_size=doc_metadata.get('file_size', 0)
                )

                all_chunks.append(chunk)
                all_metadatas.append(metadata)
                all_ids.append(chunk_id)

            total_chunks += len(chunks)

        if not all_chunks:
            return {
                'success': False,
                'message': 'No valid content to process',
                'total_chunks': 0,
                'total_documents': 0
            }

        # Generate embeddings in batch (much faster)
        print(f"[EMBED] Generating embeddings for {len(all_chunks)} chunks...")
        all_embeddings = embedding_service.embed_batch(all_chunks)

        # Store in ChromaDB
        print(f"[STORE] Storing in vector database...")
        self.collection.add(
            ids=all_ids,
            embeddings=all_embeddings,
            documents=all_chunks,
            metadatas=all_metadatas
        )

        return {
            'success': True,
            'message': 'Documents added successfully',
            'total_chunks': total_chunks,
            'total_documents': len(documents)
        }

    def query(
            self,
            query_text: str,
            n_results: int = None,
            filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks using semantic similarity.

        This is the RAG retrieval step - finds most relevant context.

        Args:
            query_text: User's question or prompt
            n_results: Number of results to return (default: TOP_K_RESULTS)
            filter_dict: Optional metadata filter (e.g., {'source_document': 'spec.md'})

        Returns:
            List of dicts with: text, metadata, score

        Example:
            results = vector_store.query("discount code validation", n_results=5)
            for result in results:
                print(result['text'])
                print(result['source_document'])
        """
        if n_results is None:
            n_results = settings.TOP_K_RESULTS

        # Generate embedding for query
        query_embedding = embedding_service.embed_text(query_text)

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict  # Optional filtering by metadata
        )

        # Format results
        formatted_results = []

        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'source_document': results['metadatas'][0][i].get('source_document', 'unknown')
                })

        return formatted_results

    def get_all_documents(self) -> List[str]:
        """
        Get list of all unique source documents in the database.
        Useful for UI display.

        Returns:
            List of document filenames
        """
        # Get all items (limit to reasonable number)
        results = self.collection.get(limit=10000)

        # Extract unique source documents
        sources = set()
        if results['metadatas']:
            for metadata in results['metadatas']:
                source = metadata.get('source_document')
                if source:
                    sources.add(source)

        return sorted(list(sources))

    def clear_collection(self):
        """
        Delete all documents from the collection.
        Useful for rebuilding knowledge base from scratch.
        """
        # Delete and recreate collection
        self.client.delete_collection(name=settings.COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        print("[OK] Vector store cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.

        Returns:
            Dict with: total_chunks, total_documents, collection_name
        """
        count = self.collection.count()
        documents = self.get_all_documents()

        return {
            'total_chunks': count,
            'total_documents': len(documents),
            'collection_name': settings.COLLECTION_NAME,
            'documents': documents
        }


# Singleton instance
vector_store = VectorStore()