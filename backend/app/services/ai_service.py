def detect_type(text):
    text = text.lower()
    if "resume" in text or "education" in text:
        return "Resume"
    if "policy" in text or "compliance" in text:
        return "Policy"
    if "agreement" in text:
        return "Legal"
    return "General"

async def analyze_document(text: str):
    if not text:
        return {
            "risk_score": 50,
            "compliance_score": 50,
            "confidence_score": 60,
            "summary": "No content",
            "issues": [],
            "document_type": "Unknown"
        }

    issues = []

    if "password" in text.lower():
        issues.append({
            "title": "Sensitive Data",
            "severity": "high",
            "description": "Possible credential leak",
            "recommendation": "Remove sensitive data"
        })

    return {
        "risk_score": 40 + len(issues)*10,
        "compliance_score": 70 - len(issues)*5,
        "confidence_score": 80,
        "summary": text[:300],
        "issues": issues,
        "document_type": detect_type(text)
    }
