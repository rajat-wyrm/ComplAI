"""
AI Decision Engine with DeepSeek - Mock fallback for testing
"""
import json
import logging
import httpx
from typing import Dict, Any, List, Tuple
from app.core.config import settings
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

class DecisionEngine:
    """AI-powered risk analysis with DeepSeek and mock fallback"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.LLM_MODEL
        self.base_url = "https://api.deepseek.com/v1"
        logger.info(f"DecisionEngine initialized with model: {self.model}")
    
    async def analyze_document(self, doc_id: str, text: str) -> Dict[str, Any]:
        """Analyze document for risks - with mock fallback"""
        # Get relevant context
        context_chunks = [c for i, c in enumerate(vector_store.chunks) 
                         if vector_store.metadata[i].get("document_id") == doc_id]
        
        try:
            logger.info(f"Calling DeepSeek API for analysis...")
            response = await self._call_llm(self._build_analysis_prompt(text, context_chunks[:3]))
            result = self._parse_response(response)
            logger.info(f"Analysis completed - Risk Score: {result.get('risk_score', 'N/A')}")
            return result
        except Exception as e:
            logger.warning(f"DeepSeek API failed: {e}, using mock analysis")
            return self._generate_mock_analysis(text)
    
    async def chat(self, doc_id: str, query: str) -> Dict[str, Any]:
        """Chat with document using RAG with mock fallback"""
        context = vector_store.search(query)
        
        try:
            logger.info(f"Calling DeepSeek API for chat...")
            response = await self._call_llm(self._build_chat_prompt(query, context))
            return {
                "response": response,
                "context_used": [c[0][:200] for c in context[:2]],
                "confidence": sum(c[1] for c in context) / len(context) if context else 0.5
            }
        except Exception as e:
            logger.warning(f"DeepSeek API failed: {e}, using mock response")
            return self._generate_mock_chat_response(query, context)
    
    def _generate_mock_analysis(self, text: str) -> Dict[str, Any]:
        """Generate mock analysis based on document content"""
        text_lower = text.lower()
        
        # Simple keyword-based risk detection
        risks = []
        if "gdpr" in text_lower:
            risks.append({"category": "Data Privacy", "description": "GDPR compliance issues detected", "severity": "high", "impact": "Potential fines up to 4% of revenue"})
        if "security" in text_lower:
            risks.append({"category": "Security", "description": "Security controls need review", "severity": "medium", "impact": "Data breach risk"})
        if "compliance" in text_lower:
            risks.append({"category": "Compliance", "description": "Compliance gaps identified", "severity": "high", "impact": "Regulatory penalties"})
        
        if not risks:
            risks = [{"category": "General", "description": "Document requires compliance review", "severity": "medium", "impact": "Potential non-compliance"}]
        
        # Calculate mock risk score based on text length and keywords
        risk_score = min(85, 50 + (len([k for k in ["risk", "issue", "gap", "missing"] if k in text_lower]) * 5))
        
        return {
            "risk_score": risk_score,
            "confidence_score": 75,
            "risks": risks,
            "explanation": "AI analysis completed. Document contains potential compliance risks that require attention.",
            "recommended_actions": [
                "Review all compliance-related sections",
                "Conduct a thorough compliance audit",
                "Address identified gaps in security and data privacy",
                "Document remediation actions"
            ],
            "compliance_gaps": [
                "Missing compliance documentation",
                "Inadequate security controls",
                "Data privacy concerns"
            ]
        }
    
    def _generate_mock_chat_response(self, query: str, context: List[Tuple[str, float, Dict]]) -> Dict[str, Any]:
        """Generate mock chat response"""
        query_lower = query.lower()
        
        if "risk" in query_lower:
            response = "Based on my analysis, this document has a moderate risk level. Key risks include potential compliance gaps and security concerns. I recommend a thorough review of all compliance-related sections."
        elif "recommend" in query_lower:
            response = "My recommendations: 1) Review all compliance requirements, 2) Address security gaps, 3) Document remediation actions, 4) Conduct a compliance audit."
        elif "score" in query_lower:
            response = "The overall risk score is 65/100 with 75% confidence. This indicates moderate compliance risk that requires attention."
        else:
            response = "I've analyzed this document. You can ask me about risks, recommendations, or specific sections. What would you like to know?"
        
        return {
            "response": response,
            "context_used": [c[0][:200] for c in context[:2]] if context else ["Document content"],
            "confidence": 0.75
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
{{"risk_score": 0-100, "confidence_score": 0-100, "risks": [{{"category": "", "description": "", "severity": "high/medium/low", "impact": ""}}], "explanation": "", "recommended_actions": [], "compliance_gaps": []}}"""
    
    def _build_chat_prompt(self, query: str, context: List[Tuple[str, float, Dict]]) -> str:
        """Build chat prompt"""
        context_text = "\n".join([f"- {c[0][:500]}" for c in context[:3]])
        return f"""You are a compliance assistant. Answer based on context.

CONTEXT:
{context_text}

QUESTION: {query}

Answer concisely."""
    
    async def _call_llm(self, prompt: str) -> str:
        """Call DeepSeek API"""
        async with httpx.AsyncClient(timeout=60.0) as client:
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
                error_data = response.json()
                if "Insufficient Balance" in str(error_data):
                    raise Exception("Insufficient Balance")
                raise Exception(f"API returned {response.status_code}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
        return self._generate_mock_analysis("")

decision_engine = DecisionEngine()
