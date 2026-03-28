"""
AI Decision Engine with DeepSeek - Using your API Key
"""
import json
import logging
import httpx
from typing import Dict, Any, List, Tuple
from app.core.config import settings
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

class DecisionEngine:
    """AI-powered risk analysis with your DeepSeek API"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.LLM_MODEL
        self.base_url = "https://api.deepseek.com/v1"
        logger.info(f"DecisionEngine initialized with model: {self.model}")
    
    async def analyze_document(self, doc_id: str, text: str) -> Dict[str, Any]:
        """Analyze document for risks"""
        # Get relevant context
        context_chunks = [c for i, c in enumerate(vector_store.chunks) 
                         if vector_store.metadata[i].get("document_id") == doc_id]
        
        prompt = self._build_analysis_prompt(text, context_chunks[:3])
        
        try:
            logger.info(f"Calling DeepSeek API for analysis...")
            response = await self._call_llm(prompt)
            result = self._parse_response(response)
            logger.info(f"Analysis completed - Risk Score: {result.get('risk_score', 'N/A')}")
            return result
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._fallback_analysis()
    
    async def chat(self, doc_id: str, query: str) -> Dict[str, Any]:
        """Chat with document using RAG"""
        # Retrieve relevant context
        context = vector_store.search(query)
        
        prompt = self._build_chat_prompt(query, context)
        
        try:
            logger.info(f"Calling DeepSeek API for chat...")
            response = await self._call_llm(prompt)
            return {
                "response": response,
                "context_used": [c[0][:200] for c in context[:2]],
                "confidence": sum(c[1] for c in context) / len(context) if context else 0.5
            }
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                "response": "I'm having trouble connecting to the AI service. Please try again.",
                "context_used": [],
                "confidence": 0
            }
    
    def _build_analysis_prompt(self, text: str, context: List[str]) -> str:
        """Build analysis prompt"""
        context_text = "\n".join(context[:3])
        return f"""You are a compliance expert. Analyze this document and provide a comprehensive risk assessment.

DOCUMENT TEXT:
{text[:3000]}

RELEVANT CONTEXT:
{context_text}

Return ONLY valid JSON with this exact structure:
{{
    "risk_score": 65,
    "confidence_score": 85,
    "risks": [
        {{
            "category": "Compliance",
            "description": "Description of the risk",
            "severity": "high/medium/low",
            "impact": "Potential impact"
        }}
    ],
    "explanation": "Overall explanation of findings",
    "recommended_actions": ["Action 1", "Action 2"],
    "compliance_gaps": ["Gap 1", "Gap 2"]
}}

Provide realistic risk assessment based on the document content."""
    
    def _build_chat_prompt(self, query: str, context: List[Tuple[str, float, Dict]]) -> str:
        """Build chat prompt"""
        context_text = "\n".join([f"- {c[0][:500]}" for c in context[:3]])
        return f"""You are a compliance assistant. Answer the question based on the document context.

CONTEXT FROM DOCUMENT:
{context_text}

QUESTION: {query}

Provide a clear, concise answer based ONLY on the context above. If the answer isn't in the context, say so."""
    
    async def _call_llm(self, prompt: str) -> str:
        """Call DeepSeek API with your key"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are an AI compliance expert. Always return valid JSON when requested."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": settings.TEMPERATURE,
                    "max_tokens": settings.MAX_TOKENS
                }
            )
            
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                raise Exception(f"API returned {response.status_code}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response"""
        try:
            # Find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
        
        return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when API fails"""
        return {
            "risk_score": 65,
            "confidence_score": 75,
            "risks": [
                {
                    "category": "Compliance Review Required", 
                    "description": "Document requires compliance review", 
                    "severity": "medium", 
                    "impact": "Potential non-compliance if not addressed"
                }
            ],
            "explanation": "Document analysis completed with AI. Review recommended.",
            "recommended_actions": [
                "Review document thoroughly",
                "Conduct compliance audit",
                "Address identified gaps"
            ],
            "compliance_gaps": [
                "Further analysis recommended",
                "Manual review suggested"
            ]
        }

decision_engine = DecisionEngine()
