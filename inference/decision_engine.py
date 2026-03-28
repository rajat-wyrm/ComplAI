\"\"\"
AI Decision Engine for risk assessment
\"\"\"
import logging
import json
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx
from app.core.config import settings
from app.core.exceptions import LLMError
from rag.rag_engine import rag_engine

logger = logging.getLogger(__name__)

class DecisionEngine:
    \"\"\"Generate risk assessments and actionable decisions\"\"\"
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.LLM_MODEL
        self.base_url = "https://api.deepseek.com/v1"
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def analyze_document(self, document_id: str, document_text: str) -> Dict[str, Any]:
        \"\"\"Analyze document for compliance risks\"\"\"
        try:
            # Get relevant context from RAG
            context_chunks = rag_engine.get_document_context(document_id)
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(document_text, context_chunks)
            
            # Call LLM
            response = await self._call_llm(prompt)
            
            # Parse response
            analysis = self._parse_analysis_response(response)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            raise LLMError(f"Analysis failed: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def chat_query(self, query: str, document_id: str) -> Dict[str, Any]:
        \"\"\"Handle chat queries about documents\"\"\"
        try:
            # Retrieve relevant context
            context = rag_engine.retrieve_context(query)
            
            # Build chat prompt
            prompt = self._build_chat_prompt(query, context)
            
            # Call LLM
            response = await self._call_llm(prompt)
            
            return {
                "response": response,
                "context_used": [ctx["text"][:200] for ctx in context[:3]],
                "confidence": self._calculate_confidence(context)
            }
            
        except Exception as e:
            logger.error(f"Chat query failed: {e}")
            raise LLMError(f"Chat failed: {str(e)}")
    
    def _build_analysis_prompt(self, text: str, context: List[str]) -> str:
        \"\"\"Build analysis prompt for document\"\"\"
        prompt = f"""You are an expert AI Compliance and Risk Analyst. Analyze this document and provide a comprehensive risk assessment.

DOCUMENT TEXT:
{text[:3000]}

RELEVANT CONTEXT:
{chr(10).join(context[:5])}

Provide analysis in the following JSON format:
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
    "recommended_actions": [
        "action 1",
        "action 2"
    ],
    "compliance_gaps": [
        "gap 1",
        "gap 2"
    ]
}}

Return ONLY valid JSON, no other text."""
        return prompt
    
    def _build_chat_prompt(self, query: str, context: List[Dict]) -> str:
        \"\"\"Build prompt for chat\"\"\"
        context_text = ""
        for i, ctx in enumerate(context):
            context_text += f"\nDocument Chunk {i+1}: {ctx['text'][:500]}...\n"
        
        prompt = f"""You are an AI Compliance Assistant. Answer questions based on the document context.

CONTEXT:
{context_text}

USER QUESTION: {query}

Provide a clear, concise answer based ONLY on the context. If the answer isn't in the context, say so.

ANSWER:"""
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        \"\"\"Call DeepSeek API\"\"\"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are an AI Compliance and Risk Analysis expert."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": settings.TEMPERATURE,
                    "max_tokens": settings.MAX_TOKENS
                }
            )
            
            if response.status_code != 200:
                logger.error(f"LLM API error: {response.text}")
                raise LLMError(f"API returned {response.status_code}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        \"\"\"Parse LLM response into structured format\"\"\"
        try:
            # Try to parse JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback to default structure
                return {
                    "risk_score": 50,
                    "confidence_score": 70,
                    "risks": [{"category": "General", "description": "Analysis completed"}],
                    "explanation": response[:500],
                    "recommended_actions": ["Review document thoroughly"],
                    "compliance_gaps": ["Further analysis recommended"]
                }
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return {
                "risk_score": 50,
                "confidence_score": 50,
                "risks": [],
                "explanation": response[:500],
                "recommended_actions": ["Manual review recommended"],
                "compliance_gaps": ["Unable to parse AI response"]
            }
    
    def _calculate_confidence(self, context: List[Dict]) -> float:
        \"\"\"Calculate confidence score based on retrieved context\"\"\"
        if not context:
            return 0.0
        
        avg_score = sum(ctx["score"] for ctx in context) / len(context)
        return min(100.0, avg_score * 100)

decision_engine = DecisionEngine()
