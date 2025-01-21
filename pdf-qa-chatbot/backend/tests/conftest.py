"""
Common test fixtures and configurations for the test suite.
"""
import os
import pytest
from unittest.mock import Mock, patch

@pytest.fixture(autouse=True)
def mock_openai_key():
    """Mock OpenAI API key for all tests."""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        yield

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n72 712 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000254 00000 n\n0000000332 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n427\n%%EOF"

@pytest.fixture
def mock_openai_embedding_response():
    """Mock OpenAI embedding API response."""
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1] * 1536)]
    return mock_response

@pytest.fixture
def mock_openai_chat_response():
    """Mock OpenAI chat completion API response."""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test answer"))]
    return mock_response