import re
from typing import Dict, Any
import os

class DocumentProcessor:
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        # Detect file type
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            text = self._extract_pdf(file_path)
        elif ext == '.docx':
            text = self._extract_docx(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        company_name = self._detect_company(text)
        doc_type = self._detect_document_type(text)
        dates = self._detect_dates(text)
        clauses = self._extract_clauses(text)
        headings = self._extract_headings(text)
        
        return {
            'full_text': text,
            'company_name': company_name,
            'document_type': doc_type,
            'word_count': len(text.split()),
            'character_count': len(text),
            'dates': dates,
            'clauses': clauses,
            'headings': headings
        }
    
    def _extract_pdf(self, file_path: str) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            return f"[Error extracting PDF: {e}]"
    
    def _extract_docx(self, file_path: str) -> str:
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text
        except Exception as e:
            return f"[Error extracting DOCX: {e}]"
    
    def _detect_company(self, text: str) -> str:
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
        return "Unknown Company"
    
    def _detect_document_type(self, text: str) -> str:
        text_lower = text.lower()
        if "resume" in text_lower or "cv" in text_lower:
            return "Resume"
        elif "policy" in text_lower or "procedure" in text_lower:
            return "Policy"
        elif "contract" in text_lower or "agreement" in text_lower:
            return "Legal Contract"
        elif "report" in text_lower or "analysis" in text_lower:
            return "Report"
        elif "notes" in text_lower:
            return "Notes"
        else:
            return "Document"
    
    def _detect_dates(self, text: str) -> list:
        pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        return re.findall(pattern, text)
    
    def _extract_clauses(self, text: str) -> list:
        # Simple clause extraction
        clause_pattern = r'(Clause|Section|Article)\s+\d+[.:]\s+[^.\n]{10,300}[.\n]'
        return re.findall(clause_pattern, text, re.IGNORECASE)
    
    def _extract_headings(self, text: str) -> list:
        heading_pattern = r'^([A-Z][A-Z\s]{5,50}|[A-Z][a-z\s]{5,60}):?$'
        headings = []
        for line in text.split('\n'):
            if re.match(heading_pattern, line.strip()):
                headings.append(line.strip())
        return headings
