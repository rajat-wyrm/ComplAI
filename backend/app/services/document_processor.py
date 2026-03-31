import os
import re
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
from docx import Document
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def extract_text_from_pdf(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise

    def extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise

    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return self.extract_text_from_docx(file_path)
        else:
            # Assume text file
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

    def detect_company_name(self, text: str) -> Optional[str]:
        # Improved detection
        patterns = [
            r'Company\s*Name:?\s*([^\n]+)',
            r'Organization\s*Name:?\s*([^\n]+)',
            r'Registered\s*Name:?\s*([^\n]+)',
            r'(?:The\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Private\s+Limited|\s+Limited|\s+Pvt\.?\s+Ltd\.?))',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        # Fallback: first line that looks like a name
        lines = text.split('\n')[:20]
        for line in lines:
            if len(line) < 100 and any(w in line.lower() for w in ['company', 'organization', 'pvt', 'ltd', 'limited', 'inc']):
                return line.strip()
        return "Unknown Company"

    def detect_dates(self, text: str) -> List[str]:
        date_patterns = [
            r'\d{2}[/-]\d{2}[/-]\d{4}',
            r'\d{4}[/-]\d{2}[/-]\d{2}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
        ]
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        return list(set(dates))

    def extract_clauses(self, text: str) -> List[str]:
        clause_patterns = [
            r'(\d+\.\d+\.?\d*\s+[A-Z][^.\n]{10,200}[.\n])',
            r'(Clause\s+\d+[.:]\s+[^.\n]{20,300}[.\n])',
            r'(Section\s+\d+[.:]\s+[^.\n]{20,300}[.\n])',
        ]
        clauses = []
        for pattern in clause_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            clauses.extend(matches)
        return clauses[:20]

    def detect_headings(self, text: str) -> List[str]:
        heading_pattern = r'^([A-Z][A-Z\s]{5,50}|[A-Z][a-z\s]{5,60}):?$'
        headings = []
        for line in text.split('\n'):
            if re.match(heading_pattern, line.strip()):
                headings.append(line.strip())
        return headings[:15]

    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        text = self.extract_text(file_path)
        return {
            'full_text': text,
            'company_name': self.detect_company_name(text),
            'dates': self.detect_dates(text),
            'clauses': self.extract_clauses(text),
            'headings': self.detect_headings(text),
            'word_count': len(text.split()),
            'character_count': len(text),
        }
