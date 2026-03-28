"""
FAISS vector store for embeddings
"""
import numpy as np
import faiss
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """FAISS-based vector store"""
    
    def __init__(self):
        self.index = None
        self.chunks = []
        self.metadata = []
        self.model = None
        self.dimension = 384
        self.vectors_dir = Path("vectors")
        self.vectors_dir.mkdir(exist_ok=True)
    
    def load_model(self):
        """Load embedding model"""
        if self.model is None:
            logger.info(f"Loading model: {settings.EMBEDDING_MODEL}")
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self.dimension = self.model.get_sentence_embedding_dimension()
        return self.model
    
    def create_index(self):
        """Create FAISS index"""
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info(f"Created index with dimension {self.dimension}")
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings"""
        model = self.load_model()
        return model.encode(texts, convert_to_numpy=True)
    
    def add_document(self, doc_id: str, chunks: List[str]):
        """Add document chunks to index"""
        if self.index is None:
            self.create_index()
        
        if not chunks:
            return
        
        embeddings = self.embed(chunks)
        self.index.add(embeddings)
        
        for i, chunk in enumerate(chunks):
            self.chunks.append(chunk)
            self.metadata.append({
                "document_id": doc_id,
                "chunk_index": i
            })
        
        logger.info(f"Added {len(chunks)} chunks for {doc_id}")
        self.save()
    
    def search(self, query: str, top_k: int = None) -> List[Tuple[str, float, Dict]]:
        """Search for relevant chunks"""
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL
        
        if self.index is None or self.index.ntotal == 0:
            return []
        
        query_embedding = self.embed([query])
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.chunks):
                similarity = 1.0 / (1.0 + distances[0][i])
                results.append((self.chunks[idx], similarity, self.metadata[idx]))
        
        return results
    
    def save(self):
        """Save index to disk"""
        if self.index is not None:
            index_path = self.vectors_dir / "faiss.index"
            faiss.write_index(self.index, str(index_path))
            
            data_path = self.vectors_dir / "data.pkl"
            with open(data_path, 'wb') as f:
                pickle.dump({
                    'chunks': self.chunks,
                    'metadata': self.metadata
                }, f)
    
    def load(self):
        """Load index from disk"""
        index_path = self.vectors_dir / "faiss.index"
        data_path = self.vectors_dir / "data.pkl"
        
        if index_path.exists() and data_path.exists():
            self.index = faiss.read_index(str(index_path))
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.metadata = data['metadata']
            logger.info(f"Loaded index with {self.index.ntotal} vectors")
            return True
        return False

vector_store = VectorStore()
