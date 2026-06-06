import json
import asyncio
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from dotenv import load_dotenv
import os

# Try to import transformers for local fallback
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

load_dotenv()
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.deepseek_client = None
        self.openai_client = None
        self.local_model = None

        if self.deepseek_api_key and self.deepseek_api_key != 'sk-placeholder':
            self.deepseek_client = AsyncOpenAI(
                api_key=self.deepseek_api_key,
                base_url="https://api.deepseek.com/v1"
            )
            logger.info("DeepSeek client initialized")
        if self.openai_api_key and self.openai_api_key != 'sk-placeholder-openai-key-if-needed':
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
            logger.info("OpenAI client initialized")

        if HAS_TRANSFORMERS:
            try:
                self.local_model = pipeline(
                    "text2text-generation",
                    model="google/flan-t5-small",
                    device=-1
                )
                logger.info("Local HuggingFace model loaded")
            except Exception as e:
                logger.warning(f"Local model failed: {e}")

    def get_system_prompt(self) -> str:
        return """
You are an expert Compliance & Risk Auditor AI. Your task is to analyze ANY document and produce a structured JSON report. Always output valid JSON.

You must handle two scenarios:

1. **Document is related to compliance/risk** (e.g., contracts, policies, legal documents, security reports, etc.)
   - Identify the document type accurately.
   - Assess risk_score (0-100, higher = more risk).
   - Assess compliance_score (0-100, higher = better compliance).
   - List issues with severity (Low/Medium/High), category, description, and specific recommendation.
   - Provide a summary.
   - List actionable recommendations.
   - List missing elements that would improve compliance.

2. **Document is NOT directly compliance-related** (e.g., resumes, meeting notes, random text, code, etc.)
   - Still produce the full JSON structure.
   - Document type should reflect the actual content (e.g., "Resume", "Meeting Notes").
   - Risk_score and compliance_score should reflect how far the document is from being a compliance document (e.g., low score if unrelated).
   - Issues should explain why it is not compliance‑ready.
   - Recommendations should suggest what the user should add to make it compliance‑related.
   - Missing elements should list the key compliance components missing.
   - Include an extra field "out_of_domain_advice" explaining how to use this for compliance purposes.

Always return JSON with the following keys (no extra text outside the JSON):
{
  "company_name": string,
  "document_type": string,
  "risk_score": integer (0-100),
  "compliance_score": integer (0-100),
  "confidence_score": integer (0-100),
  "issues": [
    {
      "title": string,
      "severity": "Low" | "Medium" | "High",
      "category": string,
      "description": string,
      "recommendation": string
    }
  ],
  "summary": string,
  "recommendations": [string],
  "missing_elements": [string],
  "out_of_domain_advice": string (optional, but include if document not compliance-related)
}
"""

    def get_analysis_prompt(self, document_text: str, context: str = "") -> str:
        text = document_text[:3500]  # increased token limit
        prompt = f"""Document to analyze:
{text}
"""
        if context:
            prompt += f"""Relevant context from similar documents:
{context}

"""
        prompt += """Generate compliance analysis in the exact JSON format described. Be thorough. If the document is not compliance‑related, still produce all fields with appropriate reasoning."""
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
            temperature=0.2,  # lower temperature for more deterministic output
            max_tokens=2500,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        # Attempt to extract JSON if there's any extra text
        try:
            return json.loads(content)
        except:
            # Try to find JSON block
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError("Could not parse JSON from DeepSeek response")

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
            temperature=0.2,
            max_tokens=2500,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except:
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError("Could not parse JSON from OpenAI response")

    async def analyze_with_local(self, document_text: str, context: str = "") -> Dict[str, Any]:
        if not self.local_model:
            raise ValueError("Local model not available")
        prompt = self.get_analysis_prompt(document_text, context)[:512]
        result = self.local_model(prompt, max_new_tokens=500)[0]['generated_text']
        try:
            return json.loads(result)
        except:
            # Return a structured fallback
            return await self.generate_mock_analysis(document_text, "Unknown")

    async def analyze_document(self, document_text: str, context: str = "") -> Dict[str, Any]:
        # Try DeepSeek first
        if self.deepseek_client:
            try:
                return await self.analyze_with_deepseek(document_text, context)
            except Exception as e:
                logger.warning(f"DeepSeek failed: {e}")
        # Then OpenAI
        if self.openai_client:
            try:
                return await self.analyze_with_openai(document_text, context)
            except Exception as e:
                logger.warning(f"OpenAI failed: {e}")
        # Then local model
        if self.local_model:
            try:
                return await self.analyze_with_local(document_text, context)
            except Exception as e:
                logger.warning(f"Local model failed: {e}")
        # Finally mock (but with detailed fallback)
        return await self.generate_mock_analysis(document_text, "Unknown")

    async def generate_mock_analysis(self, document_text: str, company_name: str = "Unknown") -> Dict[str, Any]:
        logger.info("Using enhanced mock analysis (all APIs unavailable)")
        # Simulate detection: is it compliance‑related?
        text_lower = document_text.lower()
        is_compliance = any(word in text_lower for word in ['compliance', 'risk', 'policy', 'gdpr', 'regulation', 'audit', 'security', 'legal'])
        if is_compliance:
            doc_type = "Compliance Document"
            risk_score = min(85, max(15, len(document_text) // 100))
            compliance_score = 100 - risk_score
            issues = [
                {
                    "title": "Data Privacy Compliance",
                    "severity": "Medium" if risk_score > 50 else "Low",
                    "category": "Data Privacy",
                    "description": "Document requires review for GDPR and local privacy law compliance.",
                    "recommendation": "Implement data protection impact assessment and update privacy policies."
                }
            ]
            recommendations = [
                "Review all clauses for compliance gaps",
                "Update documentation with missing policies",
                "Schedule compliance training",
                "Implement monitoring systems"
            ]
            missing_elements = [
                "Data retention policy",
                "Third-party risk assessment",
                "Incident response plan"
            ]
            out_of_domain_advice = ""
        else:
            doc_type = "Non‑Compliance Document"
            risk_score = 10  # low risk because it's not relevant
            compliance_score = 5
            issues = [
                {
                    "title": "Document not related to compliance",
                    "severity": "Low",
                    "category": "Domain mismatch",
                    "description": "The uploaded document does not appear to be a compliance, policy, or legal document.",
                    "recommendation": "For compliance analysis, please upload documents such as policies, contracts, security reports, or regulatory filings."
                }
            ]
            recommendations = [
                "Upload a compliance‑related document for risk analysis",
                "If you intend to build a compliance program, start with templates for policies and risk assessments"
            ]
            missing_elements = [
                "Compliance scope statement",
                "Relevant regulations (e.g., GDPR, HIPAA, SOC2)",
                "Risk assessment methodology"
            ]
            out_of_domain_advice = "This document is not related to compliance. To create a compliance‑ready document, include sections such as purpose, scope, roles, responsibilities, control objectives, and monitoring procedures."

        return {
            "company_name": company_name,
            "document_type": doc_type,
            "risk_score": risk_score,
            "compliance_score": compliance_score,
            "confidence_score": 65,
            "issues": issues,
            "summary": f"Document analysis shows {risk_score}% risk level and {compliance_score}% compliance score. {'This appears to be a compliance document.' if is_compliance else 'This does not appear to be a compliance document.'}",
            "recommendations": recommendations,
            "missing_elements": missing_elements,
            "out_of_domain_advice": out_of_domain_advice
        }
