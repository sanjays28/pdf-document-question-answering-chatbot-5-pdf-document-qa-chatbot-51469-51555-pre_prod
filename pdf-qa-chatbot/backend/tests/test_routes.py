"""
Tests for the FastAPI routes in the PDF QA Chatbot application.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import UploadFile
from unittest.mock import Mock, patch
from io import BytesIO

from app.main import app
from app.services.pdf_processor import PDFProcessor

client = TestClient(app)

def test_upload_valid_pdf(sample_pdf_content):
    """Test uploading a valid PDF file."""
    pdf_file = BytesIO(sample_pdf_content)
    files = {"file": ("test.pdf", pdf_file, "application/pdf")}
    
    with patch.object(PDFProcessor, 'process_file', return_value="test_file_id"):
        response = client.post("/upload", files=files)
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "PDF processed successfully",
        "file_id": "test_file_id"
    }

def test_upload_invalid_file_type():
    """Test uploading a non-PDF file."""
    text_file = BytesIO(b"This is not a PDF")
    files = {"file": ("test.txt", text_file, "text/plain")}
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 400
    assert "File must be a PDF" in response.json()["detail"]

def test_upload_empty_file():
    """Test uploading an empty file."""
    empty_file = BytesIO(b"")
    files = {"file": ("empty.pdf", empty_file, "application/pdf")}
    
    with patch.object(PDFProcessor, 'process_file', side_effect=Exception("Empty file")):
        response = client.post("/upload", files=files)
    
    assert response.status_code == 500
    assert "Empty file" in response.json()["detail"]

def test_upload_large_file():
    """Test uploading a large file."""
    # Create a large file that exceeds typical limits (e.g., 10MB)
    large_file = BytesIO(b"0" * (10 * 1024 * 1024 + 1))  # 10MB + 1 byte
    files = {"file": ("large.pdf", large_file, "application/pdf")}
    
    with patch.object(PDFProcessor, 'process_file', side_effect=Exception("File too large")):
        response = client.post("/upload", files=files)
    
    assert response.status_code == 500
    assert "File too large" in response.json()["detail"]

def test_question_valid_request():
    """Test asking a valid question."""
    question_data = {
        "question": "What is in the document?",
        "document_id": "test_doc_id"
    }
    
    with patch('app.services.qa_service.QAService.get_answer', return_value="Test answer"):
        response = client.post("/question", json=question_data)
    
    assert response.status_code == 200
    assert "answer" in response.json()
    assert response.json()["answer"] == "Test answer"

def test_question_empty_question():
    """Test asking an empty question."""
    question_data = {
        "question": "",
        "document_id": "test_doc_id"
    }
    
    response = client.post("/question", json=question_data)
    
    assert response.status_code == 400
    assert "Question cannot be empty" in response.json()["detail"]

def test_question_invalid_document_id():
    """Test asking a question for an invalid document ID."""
    question_data = {
        "question": "What is in the document?",
        "document_id": "invalid_id"
    }
    
    with patch('app.services.qa_service.QAService.get_answer', 
              side_effect=Exception("Document not found")):
        response = client.post("/question", json=question_data)
    
    assert response.status_code == 404
    assert "Document not found" in response.json()["detail"]

def test_question_no_context():
    """Test asking a question when no context is available."""
    question_data = {
        "question": "What is in the document?",
        "document_id": "test_doc_id"
    }
    
    with patch('app.services.qa_service.QAService.get_answer', 
              side_effect=Exception("No context available")):
        response = client.post("/question", json=question_data)
    
    assert response.status_code == 404
    assert "No context available" in response.json()["detail"]