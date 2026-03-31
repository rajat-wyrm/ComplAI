from typing import List, Tuple, Dict, Any
from .embedder import Embedder
from .vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = VectorStore(dimension=self.embedder.get_dimension())
    
    def add_document_chunks(self, chunks: List[str], metadata: List[Dict] = None):
        if not chunks:
            logger.warning("No chunks provided to add")
            return
        
        embeddings = self.embedder.embed_documents(chunks)
        self.vector_store.add_documents(embeddings, chunks, metadata)
    
    def retrieve(self, query: str, k: int = 5) -> List[Tuple[str, float, Dict]]:
        query_embedding = self.embedder.embed_text(query)
        results = self.vector_store.search(query_embedding, k)
        return results
    
    def save_index(self, name: str = "compliance_index"):
        self.vector_store.save(name)
    
    def load_index(self, name: str = "compliance_index"):
        return self.vector_store.load(name)
    
    def clear(self):
        self.vector_store.clear()
