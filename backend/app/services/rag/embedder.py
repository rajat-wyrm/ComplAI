from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    def embed_text(self, text: str) -> np.ndarray:
        return self.model.encode(text, normalize_embeddings=True).astype(np.float32)
    def embed_documents(self, documents: List[str]) -> np.ndarray:
        return self.model.encode(documents, normalize_embeddings=True).astype(np.float32)
    def get_dimension(self) -> int:
        return 384
