"""
FAISS vector store - simplified version
"""
import numpy as np
import pickle
import logging
from pathlib import Path
from typing import List, Tuple, Dict
import sys

logger = logging.getLogger(__name__)

class VectorStore:
    """Simple vector store for embeddings"""
    
    def __init__(self):
        self.chunks = []
        self.metadata = []
        self.vectors_dir = Path("vectors")
        self.vectors_dir.mkdir(exist_ok=True)
        self.model = None
        self._load_embeddings()
    
    def _load_embeddings(self):
        """Try to load embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded")
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e}")
            self.model = None
    
    def embed(self, texts: List[str]) -> List:
        """Generate embeddings if model available"""
        if self.model:
            return self.model.encode(texts)
        return [[0] * 384 for _ in texts]
    
    def add_document(self, doc_id: str, chunks: List[str]):
        """Add document chunks"""
        for i, chunk in enumerate(chunks):
            self.chunks.append(chunk)
            self.metadata.append({
                "document_id": doc_id,
                "chunk_index": i
            })
        
        logger.info(f"Added {len(chunks)} chunks for {doc_id}")
        self.save()
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float, Dict]]:
        """Search for relevant chunks using simple keyword matching"""
        if not self.chunks:
            return []
        
        # Simple keyword matching (fallback)
        query_words = set(query.lower().split())
        results = []
        
        for i, chunk in enumerate(self.chunks):
            chunk_words = set(chunk.lower().split())
            overlap = len(query_words & chunk_words)
            if overlap > 0:
                score = overlap / len(query_words) if query_words else 0
                results.append((chunk, min(score, 1.0), self.metadata[i]))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def save(self):
        """Save to disk"""
        data_path = self.vectors_dir / "data.pkl"
        with open(data_path, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'metadata': self.metadata
            }, f)
        logger.info(f"Saved {len(self.chunks)} chunks")
    
    def load(self):
        """Load from disk"""
        data_path = self.vectors_dir / "data.pkl"
        if data_path.exists():
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.metadata = data['metadata']
            logger.info(f"Loaded {len(self.chunks)} chunks")
            return True
        return False

vector_store = VectorStore()
