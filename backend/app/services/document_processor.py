"""
Document processing utilities
"""
import os
import logging
from pathlib import Path
import aiofiles
import PyPDF2
import pdfplumber
from docx import Document
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handle document extraction and processing"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_file(self, filename: str, file_size: int) -> bool:
        """Validate file type and size"""
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")
        if file_size > settings.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes")
        return True
    
    async def save_upload(self, content: bytes, filename: str) -> Path:
        """Save uploaded file"""
        file_path = self.upload_dir / filename
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        logger.info(f"File saved: {file_path}")
        return file_path
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text from document"""
        ext = file_path.suffix.lower()
        
        if ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif ext == '.docx':
            return self._extract_from_docx(file_path)
        elif ext == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}, trying PyPDF2")
            try:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e2:
                raise ValueError(f"PDF extraction failed: {e2}")
        
        if not text.strip():
            raise ValueError("No text extracted from PDF")
        return text
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX"""
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
        if not text.strip():
            raise ValueError("No text in DOCX document")
        return text
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        if not text.strip():
            raise ValueError("Empty text file")
        return text
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            if chunk_words:
                chunks.append(" ".join(chunk_words))
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks

processor = DocumentProcessor()
