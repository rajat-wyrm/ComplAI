import faiss
import numpy as np
from typing import List, Tuple, Dict, Any

class VectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
    def add_documents(self, embeddings: np.ndarray, documents: List[str], metadata: List[Dict] = None):
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        self.index.add(embeddings)
        self.documents.extend(documents)
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float, Dict]]:
        if self.index.ntotal == 0:
            return []
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.documents):
                results.append((self.documents[idx], float(distances[0][i]), {}))
        return results
    def save(self, name: str = "compliance_index"): pass
    def load(self, name: str = "compliance_index"): pass
