"""
RAG engine for retrieval augmented generation
"""
import logging
from typing import List, Dict, Any
from rag.vector_store import vector_store

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        self.vector_store = vector_store
        
    def retrieve_context(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        results = self.vector_store.search(query, top_k)
        
        context = []
        for chunk, score, metadata in results:
            context.append({
                "text": chunk,
                "score": score,
                "document_id": metadata.get("document_id"),
                "chunk_index": metadata.get("chunk_index")
            })
        
        return context
    
    def build_prompt(self, query: str, context: List[Dict[str, Any]]) -> str:
        prompt = """You are an AI Compliance and Risk Analysis expert. Analyze the following document context and provide a comprehensive risk assessment.

CONTEXT:
"""
        for i, ctx in enumerate(context[:5]):
            prompt += f"\n[{i+1}] {ctx['text'][:800]}...\n"
        
        prompt += f"""

QUERY: {query}

INSTRUCTIONS:
1. Identify compliance risks and gaps
2. Assign risk score (0-100)
3. Provide confidence score (0-100)
4. List specific risks with severity
5. Provide actionable recommendations

Return response in JSON format with fields: risk_score, confidence_score, risks, explanation, recommended_actions, compliance_gaps

RESPONSE:"""
        return prompt
    
    def get_document_context(self, document_id: str) -> List[str]:
        chunks = []
        for i, metadata in enumerate(self.vector_store.metadata):
            if metadata.get("document_id") == document_id:
                chunks.append(self.vector_store.chunks[i])
        return chunks

rag_engine = RAGEngine()
