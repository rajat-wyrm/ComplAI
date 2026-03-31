import re

def detect_document_type(text: str):
    text = text.lower()

    if "resume" in text or "education" in text:
        return "Resume"
    if "policy" in text or "compliance" in text:
        return "Policy Document"
    if "agreement" in text or "contract" in text:
        return "Legal Document"
    
    return "General Document"


def extract_issues(text: str):
    issues = []

    if "password" in text:
        issues.append({
            "title": "Security Risk",
            "severity": "high",
            "description": "Sensitive credential exposure",
            "recommendation": "Remove passwords or secrets"
        })

    if len(text) < 200:
        issues.append({
            "title": "Low Content",
            "severity": "low",
            "description": "Document too short",
            "recommendation": "Add more detailed content"
        })

    return issues


async def analyze_document(text: str):
    if not text:
        return {
            "risk_score": 50,
            "compliance_score": 50,
            "confidence_score": 50,
            "summary": "Empty document",
            "issues": [],
            "document_type": "Unknown"
        }

    doc_type = detect_document_type(text)
    issues = extract_issues(text)

    risk = 30 + len(issues) * 10
    compliance = 70 - len(issues) * 5

    return {
        "risk_score": min(risk, 100),
        "compliance_score": max(compliance, 0),
        "confidence_score": 80,
        "summary": text[:300],
        "issues": issues,
        "document_type": doc_type
    }
