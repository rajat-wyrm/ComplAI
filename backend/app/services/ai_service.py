async def analyze_document(text: str):
    issues = []

    if "password" in text.lower():
        issues.append({
            "title": "Security Risk",
            "severity": "high",
            "description": "Sensitive data detected",
            "recommendation": "Remove secrets"
        })

    return {
        "risk_score": 40 + len(issues)*10,
        "compliance_score": 70 - len(issues)*5,
        "confidence_score": 80,
        "summary": text[:300],
        "issues": issues,
        "document_type": "General"
    }
