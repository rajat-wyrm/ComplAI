import json
import logging
import asyncio
from typing import Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class AIService:
    def __init__(self):
        self.max_chars = 3000
        self.timeout = 10

    async def analyze_document(self, text: str) -> Dict[str, Any]:
        try:
            text = (text or "").strip()

            if not text:
                return self._invalid()

            text = text[:self.max_chars]

            raw = await asyncio.wait_for(
                self._call_ai(text),
                timeout=self.timeout
            )

            parsed = self._parse(raw)
            return parsed if parsed else self._fallback()

        except Exception as e:
            logger.error(e)
            return self._fallback()

    async def _call_ai(self, text: str) -> str:
        prompt = f"""
You are an advanced AI document analyst.

Analyze ANY type of document.

Extract:
1. What the document is about
2. Key content inside it
3. Sensitive info (login, credentials, secrets if any)
4. Compliance issues
5. Missing policies
6. Risks
7. Suggestions

Return STRICT JSON:

{{
  "document_type": "string",
  "summary": "what document contains",
  "key_points": ["point1","point2"],
  "sensitive_data": ["any passwords, credentials, api keys, etc"],
  "risk_score": number,
  "compliance_score": number,
  "confidence_score": number,
  "missing_items": ["missing policies, clauses"],
  "issues": [
    {{
      "title": "",
      "severity": "low|medium|high",
      "description": "",
      "recommendation": ""
    }}
  ]
}}

TEXT:
{text}

ONLY JSON.
"""

        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": "Return only JSON"},
                {"role": "user", "content": prompt}
            ]
        )

        return res.choices[0].message.content

    def _parse(self, text: str):
        try:
            if text.startswith("```"):
                text = text.split("```")[1]
            return json.loads(text)
        except:
            return None

    def _invalid(self):
        return {
            "document_type": "invalid",
            "summary": "Document is empty or unreadable",
            "key_points": [],
            "sensitive_data": [],
            "risk_score": 20,
            "compliance_score": 10,
            "confidence_score": 20,
            "missing_items": ["Valid content"],
            "issues": [
                {
                    "title": "Invalid Document",
                    "severity": "high",
                    "description": "No meaningful content",
                    "recommendation": "Upload proper document"
                }
            ]
        }

    def _fallback(self):
        return {
            "document_type": "unknown",
            "summary": "Fallback AI response",
            "key_points": [],
            "sensitive_data": [],
            "risk_score": 50,
            "compliance_score": 50,
            "confidence_score": 50,
            "missing_items": [],
            "issues": []
        }


ai_service = AIService()