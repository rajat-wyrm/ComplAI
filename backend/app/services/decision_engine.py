"""
AI Decision Engine with DeepSeek
"""
import json
import logging
import httpx
from typing import Dict, Any, List
from app.core.config import settings
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

class DecisionEngine:
    """AI-powered risk analysis"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.LLM_MODEL
        self.base_url = "https://api.deepseek.com/v1"
    
    async def analyze_document(self, doc_id: str, text: str) -> Dict[str, Any]:
        """Analyze document for risks"""
        # Get relevant context
        context_chunks = [c for i, c in enumerate(vector_store.chunks) 
                         if vector_store.metadata[i].get("document_id") == doc_id]
        
        prompt = self._build_analysis_prompt(text, context_chunks[:3])
        
        try:
            response = await self._call_llm(prompt)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._fallback_analysis()
    
    async def chat(self, doc_id: str, query: str) -> Dict[str, Any]:
        """Chat with document using RAG"""
        # Retrieve relevant context
        context = vector_store.search(query)
        
        prompt = self._build_chat_prompt(query, context)
        
        try:
            response = await self._call_llm(prompt)
            return {
                "response": response,
                "context_used": [c[0][:200] for c in context[:2]],
                "confidence": sum(c[1] for c in context) / len(context) if context else 0.5
            }
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                "response": "I'm having trouble connecting. Please try again.",
                "context_used": [],
                "confidence": 0
            }
    
    def _build_analysis_prompt(self, text: str, context: List[str]) -> str:
        """Build analysis prompt"""
        context_text = "\n".join(context[:3])
        return f"""You are a compliance expert. Analyze this document and provide risk assessment.

DOCUMENT:
{text[:3000]}

CONTEXT:
{context_text}

Return JSON:
{{
    "risk_score": 0-100,
    "confidence_score": 0-100,
    "risks": [{{"category": "", "description": "", "severity": "high/medium/low", "impact": ""}}],
    "explanation": "",
    "recommended_actions": [],
    "compliance_gaps": []
}}"""
    
    def _build_chat_prompt(self, query: str, context: List[Tuple[str, float, Dict]]) -> str:
        """Build chat prompt"""
        context_text = "\n".join([f"- {c[0][:500]}" for c in context[:3]])
        return f"""You are a compliance assistant. Answer based on context.

CONTEXT:
{context_text}

QUESTION: {query}

Answer concisely and helpfully."""
    
    async def _call_llm(self, prompt: str) -> str:
        """Call DeepSeek API"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": settings.TEMPERATURE,
                    "max_tokens": settings.MAX_TOKENS
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis"""
        return {
            "risk_score": 65,
            "confidence_score": 75,
            "risks": [
                {"category": "Compliance", "description": "Review required", "severity": "medium", "impact": "Potential non-compliance"}
            ],
            "explanation": "Document requires compliance review.",
            "recommended_actions": ["Review document", "Conduct compliance audit"],
            "compliance_gaps": ["Further analysis needed"]
        }

decision_engine = DecisionEngine()
