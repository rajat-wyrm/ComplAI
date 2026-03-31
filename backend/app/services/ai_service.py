import json
import logging
import os
from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.openai_api_key) if self.openai_api_key else None

    def system_prompt(self):
        return """You are an AI Compliance Risk Auditor.
Return ONLY JSON with risk_score, compliance_score, issues, summary."""

    def build_prompt(self, text: str):
        return f"""
Document:
{text[:3000]}

Return JSON:
{{
  "risk_score": number,
  "compliance_score": number,
  "issues": [
    {{
      "title": "",
      "severity": "",
      "description": "",
      "recommendation": ""
    }}
  ],
  "summary": ""
}}
"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=6))
    async def call_openai(self, text: str):
        if not self.client:
            raise Exception("No API key")

        res = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt()},
                {"role": "user", "content": self.build_prompt(text)}
            ],
            temperature=0.2
        )

        return json.loads(res.choices[0].message.content)

    async def analyze_document(self, text: str) -> Dict[str, Any]:
        try:
            result = await self.call_openai(text)
        except:
            result = {
                "risk_score": 60,
                "compliance_score": 70,
                "issues": [],
                "summary": "Fallback result"
            }

        return {
            "success": True,
            "report": {
                "risk_score": result.get("risk_score", 0),
                "compliance_score": result.get("compliance_score", 0),
                "confidence_score": 85,
                "issues": result.get("issues", []),
                "summary": result.get("summary", "")
            }
        }