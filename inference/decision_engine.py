"""
AI Decision Engine for risk assessment and actionable insights
"""
import logging
import json
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

logger = logging.getLogger(__name__)

# Import settings safely
try:
    from app.core.config import settings
except ImportError:
    class Settings:
        DEEPSEEK_API_KEY = ""
        LLM_MODEL = "deepseek-chat"
        MAX_TOKENS = 4096
        TEMPERATURE = 0.3
        TOP_K_RETRIEVAL = 5
    settings = Settings()

class DecisionEngine:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.LLM_MODEL
        self.base_url = "https://api.deepseek.com/v1"
        self.rag_engine = None
    
    def set_rag_engine(self, rag_engine):
        self.rag_engine = rag_engine
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def analyze_document(self, document_id: str, document_text: str) -> Dict[str, Any]:
        try:
            context_chunks = []
            if self.rag_engine:
                context_chunks = self.rag_engine.get_document_context(document_id)
            prompt = self._build_analysis_prompt(document_text, context_chunks)
            response = await self._call_llm(prompt)
            analysis = self._parse_analysis_response(response)
            return analysis
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return self._fallback_analysis()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def chat_query(self, query: str, document_id: str) -> Dict[str, Any]:
        try:
            context = []
            if self.rag_engine:
                context = self.rag_engine.retrieve_context(query)
            prompt = self._build_chat_prompt(query, context)
            response = await self._call_llm(prompt)
            
            return {
                "response": response,
                "context_used": [ctx["text"][:200] for ctx in context[:3]],
                "confidence": self._calculate_confidence(context)
            }
        except Exception as e:
            logger.error(f"Chat query failed: {e}")
            return {
                "response": "I'm having trouble connecting to the AI service. Please try again.",
                "context_used": [],
                "confidence": 0.0
            }
    
    def _build_analysis_prompt(self, text: str, context: List[str]) -> str:
        prompt = f"""You are an expert AI Compliance and Risk Analyst. Analyze this document and provide a comprehensive risk assessment.

DOCUMENT TEXT:
{text[:4000]}

Provide analysis in JSON format with these exact fields:
{{
    "risk_score": <number 0-100>,
    "confidence_score": <number 0-100>,
    "risks": [
        {{
            "category": "risk category",
            "description": "specific risk identified",
            "severity": "high/medium/low",
            "impact": "potential impact description"
        }}
    ],
    "explanation": "detailed explanation of findings",
    "recommended_actions": ["action 1", "action 2"],
    "compliance_gaps": ["gap 1", "gap 2"]
}}

Return ONLY valid JSON."""
        return prompt
    
    def _build_chat_prompt(self, query: str, context: List[Dict]) -> str:
        context_text = ""
        for i, ctx in enumerate(context[:3]):
            context_text += f"\nDocument Chunk {i+1}: {ctx['text'][:600]}...\n"
        
        prompt = f"""You are an AI Compliance Assistant. Answer questions based on the document context.

CONTEXT:
{context_text}

USER QUESTION: {query}

Provide a clear, concise answer based ONLY on the context. If the answer isn't in the context, say so.

ANSWER:"""
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        if not self.api_key or self.api_key == "sk-placeholder-key-replace-with-real-key":
            return self._mock_response(prompt)
        
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are an AI Compliance and Risk Analysis expert. Return valid JSON when requested."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": settings.TEMPERATURE,
                    "max_tokens": settings.MAX_TOKENS
                }
            )
            
            if response.status_code != 200:
                logger.error(f"LLM API error: {response.text}")
                return self._mock_response(prompt)
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _mock_response(self, prompt: str) -> str:
        if "risk_score" in prompt.lower():
            return json.dumps({
                "risk_score": 65,
                "confidence_score": 85,
                "risks": [
                    {"category": "Compliance", "description": "Missing documentation", "severity": "high", "impact": "Penalties"},
                    {"category": "Data Privacy", "description": "Data exposure risk", "severity": "medium", "impact": "Data breach"}
                ],
                "explanation": "Document requires compliance review.",
                "recommended_actions": ["Review compliance", "Update policies"],
                "compliance_gaps": ["Missing GDPR", "No data retention"]
            })
        return "Based on the document analysis, I recommend a compliance review."
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
        
        return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        return {
            "risk_score": 50,
            "confidence_score": 70,
            "risks": [{"category": "General", "description": "Analysis pending", "severity": "medium", "impact": "Review needed"}],
            "explanation": "Document requires manual review.",
            "recommended_actions": ["Review document manually", "Conduct compliance audit"],
            "compliance_gaps": ["Further analysis required"]
        }
    
    def _calculate_confidence(self, context: List[Dict]) -> float:
        if not context:
            return 0.0
        avg_score = sum(ctx.get("score", 0) for ctx in context) / len(context)
        return min(100.0, avg_score * 100)

decision_engine = DecisionEngine()
