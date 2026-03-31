import faiss
import numpy as np
from typing import List, Tuple, Dict, Any
import pickle
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = None
        self.documents = []
        self.metadata = []
        self.vector_path = Path("backend/vectors")
        self.vector_path.mkdir(exist_ok=True)
        self._initialize_index()
    
    def _initialize_index(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info(f"FAISS index initialized with dimension {self.dimension}")
    
    def add_documents(self, embeddings: np.ndarray, documents: List[str], metadata: List[Dict] = None):
        if self.index is None:
            self._initialize_index()
        
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        self.index.add(embeddings)
        self.documents.extend(documents)
        
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{} for _ in documents])
        
        logger.info(f"Added {len(documents)} documents to vector store. Total: {self.index.ntotal}")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float, Dict]]:
        if self.index is None or self.index.ntotal == 0:
            return []
        
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.documents):
                results.append((
                    self.documents[idx],
                    float(distances[0][i]),
                    self.metadata[idx] if idx < len(self.metadata) else {}
                ))
        
        return results
    
    def save(self, name: str = "compliance_index"):
        index_path = self.vector_path / f"{name}.faiss"
        docs_path = self.vector_path / f"{name}_docs.pkl"
        
        faiss.write_index(self.index, str(index_path))
        with open(docs_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
        
        logger.info(f"Vector store saved to {index_path}")
    
    def load(self, name: str = "compliance_index"):
        index_path = self.vector_path / f"{name}.faiss"
        docs_path = self.vector_path / f"{name}_docs.pkl"
        
        if index_path.exists() and docs_path.exists():
            self.index = faiss.read_index(str(index_path))
            with open(docs_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']
            
            logger.info(f"Loaded vector store with {self.index.ntotal} documents")
            return True
        
        return False
    
    def clear(self):
        self._initialize_index()
        self.documents = []
        self.metadata = []
        logger.info("Vector store cleared")
