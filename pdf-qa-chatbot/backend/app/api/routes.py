from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
from pydantic import BaseModel
from ..services.pdf_processor import PDFProcessor
from ..services.qa_service import QAService

router = APIRouter()
pdf_processor = PDFProcessor()
qa_service = QAService()

class QuestionRequest(BaseModel):
    question: str
    document_id: str

# PUBLIC_INTERFACE
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, str]:
    """
    Upload and process a PDF file.
    
    Args:
        file (UploadFile): The PDF file to be uploaded and processed
        
    Returns:
        Dict[str, str]: A dictionary containing the status of the upload and processing
        
    Raises:
        HTTPException: If the file is not a PDF or if there's an error in processing
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Process the PDF file
        result = await pdf_processor.process_file(file)
        return {"status": "success", "message": "PDF processed successfully", "file_id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/question")
async def ask_question(request: QuestionRequest) -> Dict[str, str]:
    """
    Process a question about a previously uploaded document.
    
    Args:
        request (QuestionRequest): The question and document ID
        
    Returns:
        Dict[str, str]: A dictionary containing the answer
        
    Raises:
        HTTPException: If the question is empty, document not found, or no context available
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        answer = await qa_service.get_answer(request.question, request.document_id)
        return {"answer": answer}
    except Exception as e:
        error_msg = str(e)
        if "Document not found" in error_msg or "No context available" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
