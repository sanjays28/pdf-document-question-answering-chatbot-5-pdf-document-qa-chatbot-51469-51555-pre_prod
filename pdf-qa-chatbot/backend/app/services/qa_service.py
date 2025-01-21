"""
Question Answering service that uses OpenAI's API to generate answers based on document context.
"""
import os
from typing import List, Dict
from openai import OpenAI
from .vector_store import VectorStore

class QAService:
    """
    Handles question answering using OpenAI's API and document context from VectorStore.
    """
    
    def __init__(self, vector_store: VectorStore):
        """
        Initialize the QA service.
        
        Args:
            vector_store: VectorStore instance for retrieving relevant document chunks
        """
        self.vector_store = vector_store
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    # PUBLIC_INTERFACE
    def get_answer(self, question: str, max_context_chunks: int = 3) -> Dict:
        """
        Generate an answer for the given question using relevant document context.
        
        Args:
            question: The question to answer
            max_context_chunks: Maximum number of context chunks to use (default: 3)
            
        Returns:
            Dict: Dictionary containing the answer and metadata
        """
        # Get relevant context chunks
        context_chunks = self.vector_store.search_similar(question, k=max_context_chunks)
        
        if not context_chunks:
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "context_used": [],
                "confidence": 0.0
            }
        
        # Prepare context for the prompt
        context_text = "\n\n".join([chunk["chunk"] for chunk in context_chunks])
        
        # Create prompt for OpenAI
        prompt = f"""Answer the question based on the following context. If the context doesn't contain enough information to answer the question confidently, say so.

Context:
{context_text}

Question: {question}

Answer:"""
        
        # Generate answer using OpenAI
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Be concise and accurate."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract answer from response
        answer = response.choices[0].message.content.strip()
        
        return {
            "answer": answer,
            "context_used": [{"text": chunk["chunk"], "doc_id": chunk["doc_id"]} for chunk in context_chunks],
            "confidence": 1.0 - min([chunk["distance"] for chunk in context_chunks]) / 2  # Simple confidence score based on vector similarity
        }