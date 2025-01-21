import pytest
import numpy as np
from unittest.mock import Mock, patch
from app.services.vector_store import VectorStore

@pytest.fixture
def vector_store():
    with patch('faiss.IndexFlatL2') as mock_index, \
         patch('openai.OpenAI') as mock_openai:
        store = VectorStore()
        # Mock the FAISS index
        store.index = Mock()
        store.index.ntotal = 0
        return store

@pytest.fixture
def mock_embedding():
    return np.random.rand(1536).astype(np.float32)

def test_generate_embeddings(vector_store):
    test_text = "Test text"
    mock_response = Mock()
    mock_response.data = [Mock(embedding=list(np.random.rand(1536)))]
    vector_store.client.embeddings.create.return_value = mock_response
    
    embedding = vector_store.generate_embeddings(test_text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (1536,)
    assert embedding.dtype == np.float32
    
    vector_store.client.embeddings.create.assert_called_once_with(
        model="text-embedding-ada-002",
        input=test_text
    )

def test_add_document_with_chunks(vector_store, mock_embedding):
    doc_id = "test-doc"
    chunks = ["chunk1", "chunk2"]
    
    with patch.object(vector_store, 'generate_embeddings', return_value=mock_embedding):
        vector_store.add_document(doc_id, chunks)
        
        # Verify document chunks are stored
        assert doc_id in vector_store.doc_chunks
        assert vector_store.doc_chunks[doc_id] == chunks
        
        # Verify embeddings were added to FAISS index
        assert vector_store.index.add.called
        added_embeddings = vector_store.index.add.call_args[0][0]
        assert added_embeddings.shape == (2, 1536)

def test_add_document_empty_chunks(vector_store):
    doc_id = "test-doc"
    vector_store.add_document(doc_id, [])
    
    assert doc_id not in vector_store.doc_chunks
    assert not vector_store.index.add.called

def test_search_similar(vector_store, mock_embedding):
    # Setup test data
    query = "test query"
    doc_id = "test-doc"
    chunks = ["chunk1", "chunk2"]
    vector_store.doc_chunks[doc_id] = chunks
    vector_store.chunk_map = {0: (doc_id, 0), 1: (doc_id, 1)}
    
    # Mock FAISS search results
    distances = np.array([[0.1, 0.2]])
    indices = np.array([[0, 1]])
    vector_store.index.search.return_value = (distances, indices)
    
    with patch.object(vector_store, 'generate_embeddings', return_value=mock_embedding):
        results = vector_store.search_similar(query, k=2)
        
        assert len(results) == 2
        assert all(isinstance(r, dict) for r in results)
        assert all(set(r.keys()) == {"doc_id", "chunk", "distance"} for r in results)
        assert results[0]["doc_id"] == doc_id
        assert results[0]["chunk"] in chunks
        assert isinstance(results[0]["distance"], float)

def test_search_similar_no_results(vector_store, mock_embedding):
    query = "test query"
    # Mock FAISS search with no results
    vector_store.index.search.return_value = (
        np.array([[-1, -1]]),
        np.array([[-1, -1]])
    )
    
    with patch.object(vector_store, 'generate_embeddings', return_value=mock_embedding):
        results = vector_store.search_similar(query, k=2)
        assert len(results) == 0

def test_search_similar_invalid_index(vector_store, mock_embedding):
    query = "test query"
    # Mock FAISS search with invalid index
    vector_store.index.search.return_value = (
        np.array([[0.1]]),
        np.array([[999]])  # Index that doesn't exist in chunk_map
    )
    
    with patch.object(vector_store, 'generate_embeddings', return_value=mock_embedding):
        results = vector_store.search_similar(query, k=1)
        assert len(results) == 0