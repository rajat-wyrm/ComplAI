\"\"\"
Document processing pipeline for PDF, DOCX, and text files
\"\"\"
import io
import os
import logging
from typing import List, Dict, Any
from pathlib import Path
import aiofiles
import PyPDF2
import pdfplumber
from docx import Document
from app.core.config import settings
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)

class DocumentProcessor:
    \"\"\"Handle document extraction and processing\"\"\"
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_file(self, filename: str, file_size: int) -> bool:
        \"\"\"Validate file type and size\"\"\"
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise DocumentProcessingError(
                f"Unsupported file type: {ext}",
                details={"allowed": list(self.ALLOWED_EXTENSIONS)}
            )
        
        if file_size > settings.MAX_FILE_SIZE:
            raise DocumentProcessingError(
                f"File too large: {file_size} bytes",
                details={"max_size": settings.MAX_FILE_SIZE}
            )
        
        return True
    
    async def save_upload(self, file_content: bytes, filename: str) -> Path:
        \"\"\"Save uploaded file to disk\"\"\"
        file_path = self.upload_dir / filename
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        logger.info(f"File saved: {file_path}")
        return file_path
    
    def extract_text(self, file_path: Path) -> str:
        \"\"\"Extract text from document based on file type\"\"\"
        ext = file_path.suffix.lower()
        
        try:
            if ext == '.pdf':
                return self._extract_from_pdf(file_path)
            elif ext == '.docx':
                return self._extract_from_docx(file_path)
            elif ext == '.txt':
                return self._extract_from_txt(file_path)
            else:
                raise DocumentProcessingError(f"Unsupported file type: {ext}")
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise DocumentProcessingError(f"Failed to extract text: {str(e)}")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        \"\"\"Extract text from PDF using multiple methods\"\"\"
        text = ""
        
        # Try pdfplumber first (better for complex PDFs)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}, trying PyPDF2")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e2:
                logger.error(f"PyPDF2 also failed: {e2}")
                raise DocumentProcessingError(f"PDF extraction failed: {e2}")
        
        if not text.strip():
            raise DocumentProcessingError("No text could be extracted from PDF")
        
        return text
    
    def _extract_from_docx(self, file_path: Path) -> str:
        \"\"\"Extract text from DOCX file\"\"\"
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            if not text.strip():
                raise DocumentProcessingError("No text in DOCX document")
            return text
        except Exception as e:
            raise DocumentProcessingError(f"DOCX extraction failed: {e}")
    
    def _extract_from_txt(self, file_path: Path) -> str:
        \"\"\"Extract text from plain text file\"\"\"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            if not text.strip():
                raise DocumentProcessingError("Empty text file")
            return text
        except Exception as e:
            raise DocumentProcessingError(f"TXT extraction failed: {e}")
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        \"\"\"Split text into overlapping chunks for RAG\"\"\"
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if overlap is None:
            overlap = settings.CHUNK_OVERLAP
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            if chunk_words:
                chunk = " ".join(chunk_words)
                chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from {len(words)} words")
        return chunks
    
    def clean_text(self, text: str) -> str:
        \"\"\"Clean and normalize text\"\"\"
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep important ones
        import re
        text = re.sub(r'[^\w\s\.\,\-\:\;\(\)\n]', '', text)
        
        return text.strip()

processor = DocumentProcessor()
