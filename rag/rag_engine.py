\"\"\"
RAG (Retrieval-Augmented Generation) Engine
\"\"\"
import logging
from typing import List, Dict, Any
from rag.vector_store import vector_store
from app.core.config import settings

logger = logging.getLogger(__name__)

class RAGEngine:
    \"\"\"Handles retrieval and context building\"\"\"
    
    def __init__(self):
        self.vector_store = vector_store
        
    def retrieve_context(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        \"\"\"Retrieve relevant context for query\"\"\"
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
        \"\"\"Build prompt with retrieved context\"\"\"
        prompt = f"""You are an AI Compliance and Risk Analysis expert. Analyze the following document context and answer the query.

CONTEXT:
"""
        for i, ctx in enumerate(context):
            prompt += f"\n[{i+1}] {ctx['text'][:500]}...\n"
        
        prompt += f"""
QUERY: {query}

INSTRUCTIONS:
1. Analyze the context thoroughly
2. Identify compliance risks and gaps
3. Provide specific recommendations
4. Include risk scores (0-100) where applicable
5. Be concise but comprehensive

RESPONSE:
"""
        return prompt
    
    def get_document_context(self, document_id: str) -> List[str]:
        \"\"\"Get all chunks for a specific document\"\"\"
        chunks = []
        for i, metadata in enumerate(self.vector_store.metadata):
            if metadata.get("document_id") == document_id:
                chunks.append(self.vector_store.chunks[i])
        return chunks

rag_engine = RAGEngine()
