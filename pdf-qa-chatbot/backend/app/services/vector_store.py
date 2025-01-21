"""
Vector store service for managing document embeddings using FAISS.
"""
import os
from typing import List, Dict
import numpy as np
import faiss
from openai import OpenAI

class VectorStore:
    """
    Handles vector embeddings generation and FAISS operations for document storage and retrieval.
    Uses OpenAI's embeddings API for generating vectors and FAISS for efficient similarity search.
    """
    
    def __init__(self):
        """Initialize the vector store with FAISS index and OpenAI client."""
        self.dimension = 1536  # OpenAI ada-002 embedding dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.doc_chunks = {}  # Map of doc_id -> list of chunk texts
        self.chunk_map = {}   # Map of FAISS index -> (doc_id, chunk_idx)

    # PUBLIC_INTERFACE
    def generate_embeddings(self, text: str) -> np.ndarray:
        """
        Generate embeddings for a given text using OpenAI's embeddings API.
        
        Args:
            text: The text to generate embeddings for
            
        Returns:
            numpy.ndarray: The generated embedding vector
        """
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return np.array(response.data[0].embedding, dtype=np.float32)

    # PUBLIC_INTERFACE
    def add_document(self, doc_id: str, chunks: List[str]) -> None:
        """
        Add document chunks to the vector store.
        
        Args:
            doc_id: Unique identifier for the document
            chunks: List of text chunks from the document
        """
        if not chunks:
            return
            
        # Generate embeddings for all chunks
        embeddings = []
        for chunk in chunks:
            embedding = self.generate_embeddings(chunk)
            embeddings.append(embedding)
            
        # Store the chunks and update the mapping
        start_idx = self.index.ntotal
        self.doc_chunks[doc_id] = chunks
        
        # Add embeddings to FAISS index
        embeddings_array = np.array(embeddings)
        self.index.add(embeddings_array)
        
        # Update chunk mapping
        for i in range(len(chunks)):
            self.chunk_map[start_idx + i] = (doc_id, i)

    # PUBLIC_INTERFACE
    def search_similar(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for similar text chunks using the query.
        
        Args:
            query: The search query text
            k: Number of similar chunks to return (default: 5)
            
        Returns:
            List[Dict]: List of dictionaries containing similar chunks and their metadata
        """
        # Generate query embedding
        query_embedding = self.generate_embeddings(query)
        
        # Perform similarity search
        distances, indices = self.index.search(
            np.array([query_embedding]), k
        )
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.chunk_map:  # -1 indicates no result found
                doc_id, chunk_idx = self.chunk_map[idx]
                results.append({
                    "doc_id": doc_id,
                    "chunk": self.doc_chunks[doc_id][chunk_idx],
                    "distance": float(distances[0][i])
                })
                
        return results