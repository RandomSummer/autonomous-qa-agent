"""
RAG (Retrieval Augmented Generation) Service
Combines vector search with LLM generation.
This is the bridge between vector DB and LLM.
"""

from typing import List, Dict, Any, Optional
from groq import Groq

from backend.config import settings
from backend.services.vector_store import vector_store


class RAGService:
    """
    Orchestrates the RAG pipeline:
    1. Retrieve relevant context from vector DB
    2. Format context for LLM
    3. Send to LLM with prompt
    4. Return response
    """

    def __init__(self):
        """Initialize Groq client for LLM calls."""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")

        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL
        print(f"[OK] RAG service initialized with model: {self.model}")

    def retrieve_context(
            self,
            query: str,
            n_results: int = None,
            filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from vector database.

        This is the "Retrieval" part of RAG.

        Args:
            query: User query or prompt
            n_results: Number of chunks to retrieve
            filter_dict: Optional metadata filter

        Returns:
            List of relevant chunks with metadata
        """
        return vector_store.query(
            query_text=query,
            n_results=n_results or settings.TOP_K_RESULTS,
            filter_dict=filter_dict
        )

    def format_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks into a context string for LLM.

        Why this format? Clear separation and source attribution.
        LLM can reference specific documents in its response.

        Args:
            retrieved_chunks: List of chunks from vector DB

        Returns:
            Formatted context string

        Example output:
            === From product_specs.md ===
            The discount code SAVE15 applies 15% discount...

            === From ui_ux_guide.txt ===
            Error messages must be red...
        """
        if not retrieved_chunks:
            return "No relevant documentation found."

        context_parts = []

        for chunk in retrieved_chunks:
            source = chunk['source_document']
            text = chunk['text']
            score = chunk['score']

            context_parts.append(f"=== From {source} (relevance: {score:.2f}) ===\n{text}\n")

        return "\n".join(context_parts)

    def generate_response(
            self,
            user_query: str,
            context: str,
            system_prompt: str,
            temperature: float = None
    ) -> str:
        """
        Generate LLM response using retrieved context.

        This is the "Generation" part of RAG.

        Args:
            user_query: User's question or request
            context: Retrieved context from vector DB
            system_prompt: Instructions for the LLM
            temperature: LLM creativity (default: 0.1 for deterministic)

        Returns:
            LLM response text
        """
        if temperature is None:
            temperature = settings.TEMPERATURE

        # Construct the full user message with context
        user_message = f"""Based on the following documentation:

{context}

User Request: {user_query}

Please respond based ONLY on the provided documentation. Do not make up or hallucinate any features not mentioned in the documents."""

        # Call Groq API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=settings.MAX_TOKENS
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")

    def rag_query(
            self,
            user_query: str,
            system_prompt: str,
            n_results: int = None,
            temperature: float = None,
            filter_dict: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline in one call.

        Steps:
        1. Retrieve relevant context
        2. Format context
        3. Generate LLM response
        4. Return everything

        Args:
            user_query: User's question
            system_prompt: LLM instructions
            n_results: Number of chunks to retrieve
            temperature: LLM creativity
            filter_dict: Optional metadata filter

        Returns:
            Dict with: response, context, retrieved_chunks

        Example:
            result = rag_service.rag_query(
                user_query="Generate test cases for discount codes",
                system_prompt="You are a QA expert..."
            )
            print(result['response'])
        """
        # Step 1: Retrieve
        retrieved_chunks = self.retrieve_context(
            query=user_query,
            n_results=n_results,
            filter_dict=filter_dict
        )

        # Step 2: Format
        context = self.format_context(retrieved_chunks)

        # Step 3: Generate
        response = self.generate_response(
            user_query=user_query,
            context=context,
            system_prompt=system_prompt,
            temperature=temperature
        )

        return {
            'response': response,
            'context': context,
            'retrieved_chunks': retrieved_chunks,
            'num_chunks': len(retrieved_chunks)
        }


# Singleton instance
rag_service = RAGService()