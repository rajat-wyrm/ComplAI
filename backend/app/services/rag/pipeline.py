from typing import List, Dict, Any
from .retriever import Retriever
import logging

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
    
    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def process_document(self, text: str, metadata: Dict = None) -> List[str]:
        chunks = self.chunk_text(text)
        
        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            meta = {
                'chunk_id': i,
                'total_chunks': len(chunks)
            }
            if metadata:
                meta.update(metadata)
            chunk_metadata.append(meta)
        
        self.retriever.add_document_chunks(chunks, chunk_metadata)
        return chunks
    
    def retrieve_context(self, query: str, k: int = 5) -> str:
        results = self.retriever.retrieve(query, k)
        
        if not results:
            return ""
        
        context_parts = []
        for i, (chunk, score, meta) in enumerate(results):
            context_parts.append(f"[Chunk {i+1} - Score: {score:.4f}]\n{chunk}")
        
        return "\n\n".join(context_parts)
    
    def save(self, name: str = "compliance_index"):
        self.retriever.save_index(name)
    
    def load(self, name: str = "compliance_index"):
        return self.retriever.load_index(name)
