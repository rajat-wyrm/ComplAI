import json
import asyncio
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.deepseek_client = None
        self.openai_client = None
        
        if self.deepseek_api_key and self.deepseek_api_key != 'sk-placeholder':
            self.deepseek_client = AsyncOpenAI(
                api_key=self.deepseek_api_key,
                base_url="https://api.deepseek.com/v1"
            )
            logger.info("DeepSeek client initialized")
        
        if self.openai_api_key and self.openai_api_key != 'sk-placeholder-openai-key-if-needed':
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
            logger.info("OpenAI client initialized")
    
    def get_system_prompt(self) -> str:
        return """You are an AI Compliance Risk Auditor.

Analyze the given document and generate a structured compliance report.

You must:
- Identify legal and compliance risks
- Assign severity (Low/Medium/High)
- Provide risk score (0-100 where 100 is highest risk)
- Provide compliance score (0-100 where 100 is fully compliant)
- Extract company name and key entities
- Suggest actionable recommendations
- Provide summary and next actions

Return ONLY JSON with no additional text."""

    def get_analysis_prompt(self, document_text: str, context: str = "") -> str:
        prompt = f"""Document to analyze:

{document_text[:3000]}

"""
        if context:
            prompt += f"""Relevant context from similar documents:
{context}

"""
        
        prompt += """Generate compliance analysis report in JSON format:
{
"company_name": "extracted company name",
"document_type": "type of document (e.g., Contract, Policy, Report, etc.)",
"risk_score": 0-100,
"compliance_score": 0-100,
"issues": [
{
"title": "issue title",
"severity": "Low/Medium/High",
"category": "category like Data Privacy, Security, Legal, etc.",
"description": "detailed description",
"recommendation": "actionable recommendation"
}
],
"summary": "brief summary of findings",
"next_actions": ["action 1", "action 2", "action 3"],
"confidence_score": 0-100
}"""
        
        return prompt

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_with_deepseek(self, document_text: str, context: str = "") -> Dict[str, Any]:
        if not self.deepseek_client:
            raise ValueError("DeepSeek client not available")
        
        try:
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
            
            result = json.loads(response.choices[0].message.content)
            logger.info("DeepSeek analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"DeepSeek analysis failed: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_with_openai(self, document_text: str, context: str = "") -> Dict[str, Any]:
        if not self.openai_client:
            raise ValueError("OpenAI client not available")
        
        try:
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
            
            result = json.loads(response.choices[0].message.content)
            logger.info("OpenAI analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            raise

    async def analyze_document(self, document_text: str, context: str = "") -> Dict[str, Any]:
        if self.deepseek_client:
            try:
                return await self.analyze_with_deepseek(document_text, context)
            except Exception as e:
                logger.warning(f"DeepSeek failed, trying OpenAI: {e}")
                if self.openai_client:
                    return await self.analyze_with_openai(document_text, context)
                raise
        
        elif self.openai_client:
            return await self.analyze_with_openai(document_text, context)
        
        else:
            raise ValueError("No AI service available. Please configure DeepSeek or OpenAI API key.")
    
    async def generate_mock_analysis(self, document_text: str, company_name: str = "Unknown") -> Dict[str, Any]:
        logger.info("Generating mock analysis as fallback")
        
        risk_score = min(85, max(15, len(document_text) // 100))
        compliance_score = 100 - risk_score
        
        return {
            "company_name": company_name,
            "document_type": "Compliance Document",
            "risk_score": risk_score,
            "compliance_score": compliance_score,
            "issues": [
                {
                    "title": "Data Privacy Compliance",
                    "severity": "Medium" if risk_score > 50 else "Low",
                    "category": "Data Privacy",
                    "description": "Document requires review for GDPR and local privacy law compliance.",
                    "recommendation": "Implement data protection impact assessment and update privacy policies."
                },
                {
                    "title": "Security Controls",
                    "severity": "High" if risk_score > 70 else "Medium",
                    "category": "Security",
                    "description": "Security measures need enhancement to meet compliance standards.",
                    "recommendation": "Conduct security audit and implement necessary controls."
                }
            ],
            "summary": f"Document analysis shows {risk_score}% risk level with focus on compliance requirements.",
            "next_actions": [
                "Review all clauses for compliance gaps",
                "Update documentation with missing policies",
                "Schedule compliance training",
                "Implement monitoring systems"
            ],
            "confidence_score": 65
        }
