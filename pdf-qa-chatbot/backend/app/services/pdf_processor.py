import PyPDF2
from fastapi import UploadFile
import uuid
from typing import List, Dict
import io

class PDFProcessor:
    def __init__(self):
        self.chunk_size = 1000  # Default chunk size in characters
        self.processed_files: Dict[str, List[str]] = {}

    # PUBLIC_INTERFACE
    async def process_file(self, file: UploadFile) -> str:
        """
        Process an uploaded PDF file by extracting text and chunking it.
        
        Args:
            file (UploadFile): The uploaded PDF file to process
            
        Returns:
            str: A unique identifier for the processed file
            
        Raises:
            Exception: If there's an error processing the PDF
        """
        try:
            # Read the uploaded file into memory
            content = await file.read()
            pdf_file = io.BytesIO(content)
            
            # Extract text from PDF
            text = self._extract_text(pdf_file)
            
            # Chunk the extracted text
            chunks = self._chunk_text(text)
            
            # Generate a unique ID for this file
            file_id = str(uuid.uuid4())
            
            # Store the chunks
            self.processed_files[file_id] = chunks
            
            return file_id
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

    def _extract_text(self, pdf_file: io.BytesIO) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_file (io.BytesIO): The PDF file in memory
            
        Returns:
            str: The extracted text
        """
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks of approximately equal size.
        
        Args:
            text (str): The text to chunk
            
        Returns:
            List[str]: List of text chunks
        """
        chunks = []
        current_chunk = ""
        
        # Split by sentences (simple approach)
        sentences = text.replace('\n', ' ').split('.')
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + '.'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '.'
                
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    # PUBLIC_INTERFACE
    def get_chunks(self, file_id: str) -> List[str]:
        """
        Retrieve the text chunks for a processed file.
        
        Args:
            file_id (str): The unique identifier of the processed file
            
        Returns:
            List[str]: List of text chunks
            
        Raises:
            KeyError: If the file_id is not found
        """
        if file_id not in self.processed_files:
            raise KeyError(f"No processed file found with ID: {file_id}")
        return self.processed_files[file_id]