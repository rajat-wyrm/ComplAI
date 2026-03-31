from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        if not self.model:
            raise ValueError("Model not initialized")
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.astype(np.float32)
    
    def embed_documents(self, documents: List[str]) -> np.ndarray:
        if not self.model:
            raise ValueError("Model not initialized")
        embeddings = self.model.encode(documents, normalize_embeddings=True)
        return embeddings.astype(np.float32)
    
    def get_dimension(self) -> int:
        return 384
