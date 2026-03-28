\"\"\"
FAISS vector store for document embeddings
\"\"\"
import numpy as np
import faiss
import pickle
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path
from sentence_transformers import SentenceTransformer
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.index = None
        self.chunks = []
        self.metadata = []
        self.embedding_model = None
        self.dimension = 384
        self.vectors_dir = Path("data/vectors")
        self.vectors_dir.mkdir(parents=True, exist_ok=True)
        
    def load_model(self):
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        return self.embedding_model
    
    def create_index(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info(f"Created FAISS index with dimension {self.dimension}")
        
    def embed_text(self, texts: List[str]) -> np.ndarray:
        model = self.load_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def add_document(self, document_id: str, chunks: List[str], metadata: Dict = None):
        if self.index is None:
            self.create_index()
        
        if not chunks:
            logger.warning(f"No chunks to add for document {document_id}")
            return
        
        embeddings = self.embed_text(chunks)
        self.index.add(embeddings)
        
        start_idx = len(self.chunks)
        for i, chunk in enumerate(chunks):
            self.chunks.append(chunk)
            self.metadata.append({
                "document_id": document_id,
                "chunk_index": start_idx + i,
                **(metadata or {})
            })
        
        logger.info(f"Added {len(chunks)} chunks for document {document_id}")
        self.save()
        
    def search(self, query: str, top_k: int = None) -> List[Tuple[str, float, Dict]]:
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL
            
        if self.index is None or self.index.ntotal == 0:
            logger.warning("No vectors in index")
            return []
        
        query_embedding = self.embed_text([query])
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.chunks):
                results.append((
                    self.chunks[idx],
                    float(1.0 / (1.0 + distances[0][i])),
                    self.metadata[idx]
                ))
        
        logger.info(f"Found {len(results)} relevant chunks for query")
        return results
    
    def save(self):
        if self.index is not None:
            index_path = self.vectors_dir / "faiss.index"
            faiss.write_index(self.index, str(index_path))
            
            data_path = self.vectors_dir / "chunks.pkl"
            with open(data_path, 'wb') as f:
                pickle.dump({
                    'chunks': self.chunks,
                    'metadata': self.metadata
                }, f)
            
            logger.info(f"Saved vector store to {self.vectors_dir}")
    
    def load(self):
        index_path = self.vectors_dir / "faiss.index"
        data_path = self.vectors_dir / "chunks.pkl"
        
        if index_path.exists() and data_path.exists():
            self.index = faiss.read_index(str(index_path))
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.metadata = data['metadata']
            logger.info(f"Loaded vector store with {self.index.ntotal} vectors")
            return True
        else:
            logger.info("No existing vector store found")
            return False

vector_store = VectorStore()

async def init_vector_store():
    vector_store.load()
    if vector_store.index is None:
        vector_store.create_index()
    logger.info("Vector store initialized")
