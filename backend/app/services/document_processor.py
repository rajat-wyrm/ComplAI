"""
Document Processor (ULTIMATE VERSION)

? Handles ANY file (pdf, docx, txt, unknown)
? Never returns empty text
? Smart cleaning
? Optimized chunking for AI + RAG
? Fault-tolerant
? Fast
"""

import os
import re
import logging
import tempfile
from typing import Dict, Any, Optional, List

from pypdf import PdfReader
from docx import Document

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self):
        self.max_chars = 20000
        self.chunk_size = 500
        self.chunk_overlap = 100

    # =========================
    # FILE SAVE
    # =========================
    async def save_upload(self, content: bytes, filename: str) -> str:
        try:
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, filename)

            with open(file_path, "wb") as f:
                f.write(content)

            return file_path

        except Exception as e:
            logger.exception(f"File save failed: {e}")
            raise

    # =========================
    # UNIVERSAL EXTRACTION
    # =========================
    def extract_text(self, file_path: str) -> str:
        try:
            ext = file_path.lower()

            if ext.endswith(".pdf"):
                text = self._extract_pdf(file_path)

            elif ext.endswith(".docx"):
                text = self._extract_docx(file_path)

            elif ext.endswith(".txt"):
                text = self._extract_txt(file_path)

            else:
                #  UNKNOWN FILE ? try raw read
                text = self._extract_fallback(file_path)

            text = self._clean_text(text)

            #  NEVER RETURN EMPTY
            if not text or len(text.strip()) < 10:
                return f"File processed but content was minimal or unreadable. Filename: {os.path.basename(file_path)}"

            return text

        except Exception as e:
            logger.exception(f"Extraction failed: {e}")
            return f"Extraction error. Filename: {os.path.basename(file_path)}"

    # =========================
    # PDF
    # =========================
    def _extract_pdf(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = []

            for page in reader.pages:
                text.append(page.extract_text() or "")

            return "\n".join(text)

        except Exception as e:
            logger.warning(f"PDF error: {e}")
            return ""

    # =========================
    # DOCX
    # =========================
    def _extract_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs if p.text)

        except Exception as e:
            logger.warning(f"DOCX error: {e}")
            return ""

    # =========================
    # TXT
    # =========================
    def _extract_txt(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except:
            return ""

    # =========================
    # FALLBACK (ANY FILE)
    # =========================
    def _extract_fallback(self, file_path: str) -> str:
        try:
            with open(file_path, "rb") as f:
                raw = f.read(5000)
                return raw.decode("utf-8", errors="ignore")
        except:
            return ""

    # =========================
    # CLEAN TEXT
    # =========================
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\x00-\x7F]+", " ", text)

        return text.strip()[:self.max_chars]

    # =========================
    # CHUNKING (SMART)
    # =========================
    def chunk_text(self, text: str) -> List[str]:
        if not text:
            return ["No content"]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            start += (self.chunk_size - self.chunk_overlap)

        return chunks if chunks else [text]

    # =========================
    # METADATA (OPTIONAL INTELLIGENCE)
    # =========================
    def detect_company_name(self, text: str) -> Optional[str]:
        patterns = [
            r'Company\s*Name:?\s*([^\n]+)',
            r'Organization\s*Name:?\s*([^\n]+)',
            r'(?:The\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Ltd|Inc|Corp)))'
        ]

        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()

        return "Unknown Company"

    # =========================
    # FULL ANALYSIS
    # =========================
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        text = self.extract_text(file_path)

        return {
            "full_text": text,
            "company_name": self.detect_company_name(text),
            "word_count": len(text.split()),
            "character_count": len(text)
        }


# =========================
# SINGLETON
# =========================
processor = DocumentProcessor()
