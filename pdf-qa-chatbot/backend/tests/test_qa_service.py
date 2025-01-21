import pytest
from unittest.mock import Mock, patch
from app.services.qa_service import QAService

@pytest.fixture
def mock_vector_store():
    return Mock()

@pytest.fixture
def qa_service(mock_vector_store):
    with patch('openai.OpenAI'):
        service = QAService(mock_vector_store)
        return service

def test_get_answer_with_context(qa_service, mock_vector_store):
    # Mock vector store response
    mock_vector_store.search_similar.return_value = [
        {"chunk": "Test context 1", "doc_id": "doc1", "distance": 0.1},
        {"chunk": "Test context 2", "doc_id": "doc1", "distance": 0.2}
    ]
    
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test answer"))]
    qa_service.client.chat.completions.create.return_value = mock_response
    
    # Test get_answer
    result = qa_service.get_answer("test question")
    
    assert isinstance(result, dict)
    assert "answer" in result
    assert "context_used" in result
    assert "confidence" in result
    assert result["answer"] == "Test answer"
    assert len(result["context_used"]) == 2
    assert isinstance(result["confidence"], float)
    assert 0 <= result["confidence"] <= 1

def test_get_answer_no_context(qa_service, mock_vector_store):
    # Mock vector store with no results
    mock_vector_store.search_similar.return_value = []
    
    # Test get_answer
    result = qa_service.get_answer("test question")
    
    assert isinstance(result, dict)
    assert "answer" in result
    assert "context_used" in result
    assert "confidence" in result
    assert "couldn't find any relevant information" in result["answer"].lower()
    assert len(result["context_used"]) == 0
    assert result["confidence"] == 0.0

def test_get_answer_with_max_context_chunks(qa_service, mock_vector_store):
    # Mock vector store response
    mock_chunks = [
        {"chunk": f"Test context {i}", "doc_id": "doc1", "distance": 0.1 * i}
        for i in range(5)
    ]
    mock_vector_store.search_similar.return_value = mock_chunks
    
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test answer"))]
    qa_service.client.chat.completions.create.return_value = mock_response
    
    # Test get_answer with max_context_chunks=3
    result = qa_service.get_answer("test question", max_context_chunks=3)
    
    assert len(result["context_used"]) == 3
    mock_vector_store.search_similar.assert_called_with("test question", k=3)

def test_get_answer_openai_prompt_format(qa_service, mock_vector_store):
    # Mock vector store response
    mock_vector_store.search_similar.return_value = [
        {"chunk": "Test context", "doc_id": "doc1", "distance": 0.1}
    ]
    
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test answer"))]
    qa_service.client.chat.completions.create.return_value = mock_response
    
    # Test get_answer
    qa_service.get_answer("test question")
    
    # Verify OpenAI API call
    create_call = qa_service.client.chat.completions.create.call_args
    assert create_call is not None
    
    # Verify model and messages format
    kwargs = create_call[1]
    assert kwargs["model"] == "gpt-3.5-turbo"
    assert len(kwargs["messages"]) == 2
    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][1]["role"] == "user"
    assert "test question" in kwargs["messages"][1]["content"]
    assert "Test context" in kwargs["messages"][1]["content"]