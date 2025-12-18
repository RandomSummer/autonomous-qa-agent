import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid
import os

class KnowledgeBase:
    """Vector database for storing and retrieving document chunks"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "qa_documents"
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def build_from_documents(self, documents: List[Dict[str, Any]]):
        """Build knowledge base from processed documents"""
        try:
            # Clear existing collection
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            all_chunks = []
            all_embeddings = []
            all_metadatas = []
            all_ids = []
            
            for doc in documents:
                for chunk in doc['chunks']:
                    # Generate embedding
                    embedding = self.embedding_model.encode(chunk['text']).tolist()
                    
                    # Prepare metadata
                    metadata = {
                        'source': doc['filename'],
                        'content_type': doc['content_type'],
                        'chunk_index': chunk['metadata']['chunk_index']
                    }
                    
                    all_chunks.append(chunk['text'])
                    all_embeddings.append(embedding)
                    all_metadatas.append(metadata)
                    all_ids.append(str(uuid.uuid4()))
            
            # Add to collection in batch
            if all_chunks:
                self.collection.add(
                    documents=all_chunks,
                    embeddings=all_embeddings,
                    metadatas=all_metadatas,
                    ids=all_ids
                )
            
            return len(all_chunks)
            
        except Exception as e:
            raise Exception(f"Error building knowledge base: {str(e)}")
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query the knowledge base for relevant chunks"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query_text).tolist()
            
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Error querying knowledge base: {str(e)}")
    
    def get_all_sources(self) -> List[str]:
        """Get list of all source documents in the knowledge base"""
        try:
            results = self.collection.get(include=['metadatas'])
            sources = set()
            for metadata in results['metadatas']:
                sources.add(metadata['source'])
            return list(sources)
        except:
            return []
    
    def clear(self):
        """Clear the knowledge base"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            raise Exception(f"Error clearing knowledge base: {str(e)}")