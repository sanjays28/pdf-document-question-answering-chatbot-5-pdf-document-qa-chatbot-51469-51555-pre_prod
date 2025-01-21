import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from app.services.pdf_processor import PDFProcessor

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

@pytest.fixture
def mock_pdf_file():
    # Create a mock UploadFile object
    mock_file = Mock()
    mock_file.read = MagicMock(return_value=b"mock pdf content")
    return mock_file

@pytest.mark.asyncio
async def test_process_file_valid_pdf(pdf_processor, mock_pdf_file):
    with patch('PyPDF2.PdfReader') as mock_reader:
        # Mock PDF reader behavior
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test content page 1"
        mock_reader.return_value.pages = [mock_page]
        
        # Process the mock file
        file_id = await pdf_processor.process_file(mock_pdf_file)
        
        # Verify file ID is generated and chunks are stored
        assert isinstance(file_id, str)
        assert len(file_id) > 0
        assert file_id in pdf_processor.processed_files
        assert len(pdf_processor.processed_files[file_id]) > 0

@pytest.mark.asyncio
async def test_process_file_invalid_pdf(pdf_processor):
    mock_file = Mock()
    mock_file.read = MagicMock(side_effect=Exception("Invalid PDF"))
    
    with pytest.raises(Exception) as exc_info:
        await pdf_processor.process_file(mock_file)
    assert "Error processing PDF" in str(exc_info.value)

def test_extract_text_valid_pdf(pdf_processor):
    with patch('PyPDF2.PdfReader') as mock_reader:
        # Mock PDF reader behavior
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test content"
        mock_reader.return_value.pages = [mock_page]
        
        # Test text extraction
        text = pdf_processor._extract_text(BytesIO(b"mock content"))
        assert text == "Test content"

def test_extract_text_invalid_pdf(pdf_processor):
    with pytest.raises(Exception) as exc_info:
        pdf_processor._extract_text(BytesIO(b"invalid pdf content"))
    assert "Error extracting text from PDF" in str(exc_info.value)

def test_chunk_text_with_content(pdf_processor):
    test_text = "This is a test sentence. This is another test sentence. " * 10
    chunks = pdf_processor._chunk_text(test_text)
    
    assert len(chunks) > 0
    assert all(len(chunk) <= pdf_processor.chunk_size for chunk in chunks)
    assert all(isinstance(chunk, str) for chunk in chunks)

def test_chunk_text_empty(pdf_processor):
    chunks = pdf_processor._chunk_text("")
    assert len(chunks) == 0

def test_get_chunks_valid_id(pdf_processor):
    # Setup test data
    test_chunks = ["chunk1", "chunk2"]
    file_id = "test-id"
    pdf_processor.processed_files[file_id] = test_chunks
    
    # Test retrieval
    retrieved_chunks = pdf_processor.get_chunks(file_id)
    assert retrieved_chunks == test_chunks

def test_get_chunks_invalid_id(pdf_processor):
    with pytest.raises(KeyError) as exc_info:
        pdf_processor.get_chunks("invalid-id")
    assert "No processed file found with ID" in str(exc_info.value)