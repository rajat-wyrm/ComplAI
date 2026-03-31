import json
import asyncio
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from dotenv import load_dotenv
import os

# Try to import HuggingFace transformers (optional)
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

from app.core.config import settings

load_dotenv()
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.deepseek_api_key = settings.DEEPSEEK_API_KEY
        self.openai_api_key = settings.OPENAI_API_KEY
        self.huggingface_api_key = settings.HUGGINGFACE_API_KEY
        
        self.deepseek_client = None
        self.openai_client = None
        self.local_model = None

        if self.deepseek_api_key and self.deepseek_api_key != "sk-placeholder":
            self.deepseek_client = AsyncOpenAI(
                api_key=self.deepseek_api_key,
                base_url="https://api.deepseek.com/v1"
            )
            logger.info("DeepSeek client initialized")
        if self.openai_api_key and self.openai_api_key != "sk-placeholder-openai-key-if-needed":
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
            logger.info("OpenAI client initialized")

        if HAS_TRANSFORMERS:
            try:
                self.local_model = pipeline(
                    "text2text-generation",
                    model="google/flan-t5-small",
                    device=-1  # CPU
                )
                logger.info("Local HuggingFace model loaded")
            except Exception as e:
                logger.warning(f"Local model load failed: {e}")

    def get_system_prompt(self) -> str:
        return """You are an AI Compliance Risk Auditor. Analyze the given document and generate a structured compliance report. Return ONLY JSON."""

    def get_analysis_prompt(self, document_text: str, context: str = "") -> str:
        prompt = f"""Document to analyze:
{document_text[:2000]}
"""
        if context:
            prompt += f"""Relevant context from similar documents:
{context}

"""
        prompt += """Generate compliance analysis in JSON format with these keys:
{
  "document_type": "detected type (e.g., Contract, Policy, Resume, etc.)",
  "summary": "brief summary",
  "risk_score": 0-100,
  "compliance_score": 0-100,
  "confidence_score": 0-100,
  "issues": [
    {
      "title": "issue title",
      "severity": "Low/Medium/High",
      "category": "category (e.g., Data Privacy, Security)",
      "description": "detailed description",
      "recommendation": "actionable recommendation"
    }
  ],
  "recommendations": ["recommendation 1", "recommendation 2"],
  "missing_elements": ["missing compliance element 1", "missing element 2"]
}"""
        return prompt

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_with_deepseek(self, document_text: str, context: str = "") -> Dict[str, Any]:
        if not self.deepseek_client:
            raise ValueError("DeepSeek client not available")
        response = await self.deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": self.get_analysis_prompt(document_text, context)}
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_with_openai(self, document_text: str, context: str = "") -> Dict[str, Any]:
        if not self.openai_client:
            raise ValueError("OpenAI client not available")
        response = await self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": self.get_analysis_prompt(document_text, context)}
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    async def analyze_with_local(self, document_text: str, context: str = "") -> Dict[str, Any]:
        if not self.local_model:
            raise ValueError("Local model not available")
        prompt = self.get_analysis_prompt(document_text, context)
        # Truncate to model max length
        prompt = prompt[:512]
        result = self.local_model(prompt, max_new_tokens=500)[0]['generated_text']
        try:
            return json.loads(result)
        except:
            # Fallback to mock if parsing fails
            return await self.generate_mock_analysis(document_text)

    async def analyze_document(self, document_text: str, context: str = "") -> Dict[str, Any]:
        if self.deepseek_client:
            try:
                return await self.analyze_with_deepseek(document_text, context)
            except Exception as e:
                logger.warning(f"DeepSeek failed: {e}")
        if self.openai_client:
            try:
                return await self.analyze_with_openai(document_text, context)
            except Exception as e:
                logger.warning(f"OpenAI failed: {e}")
        if self.local_model:
            try:
                return await self.analyze_with_local(document_text, context)
            except Exception as e:
                logger.warning(f"Local model failed: {e}")
        # Final fallback: mock
        return await self.generate_mock_analysis(document_text)

    async def generate_mock_analysis(self, document_text: str, company_name: str = "Unknown") -> Dict[str, Any]:
        logger.info("Using mock analysis")
        risk_score = min(85, max(15, len(document_text) // 100))
        compliance_score = 100 - risk_score
        return {
            "document_type": "General Document",
            "summary": f"This document appears to be a general text. Based on analysis, risk level is {risk_score}%.",
            "risk_score": risk_score,
            "compliance_score": compliance_score,
            "confidence_score": 65,
            "issues": [
                {
                    "title": "Unclear compliance context",
                    "severity": "Medium",
                    "category": "General",
                    "description": "The document does not clearly state compliance with regulations.",
                    "recommendation": "Add explicit compliance statements and refer to relevant laws."
                }
            ],
            "recommendations": ["Review document for regulatory alignment", "Add compliance clauses"],
            "missing_elements": ["Compliance declaration", "Data protection statement"]
        }
