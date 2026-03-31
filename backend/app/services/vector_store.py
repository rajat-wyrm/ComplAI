"""
Vector Store (PRODUCTION-GRADE - FAST + SCALABLE + HYBRID SEARCH)

- Embedding-based semantic search (SentenceTransformers)
- Keyword fallback (always works)
- Disk persistence
- Async-safe integration (used via to_thread)
"""

import os
import pickle
import logging
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.vectors_dir = Path("vectors")
        self.vectors_dir.mkdir(exist_ok=True)

        self.chunks: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray | None = None

        self.model = None
        self.embedding_dim = 384

        self._load_model()
        self._load()

    # =========================
    # MODEL LOADING
    # =========================
    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("✅ Embedding model loaded")
        except Exception as e:
            logger.warning(f"⚠️ Embedding model unavailable: {e}")
            self.model = None

    # =========================
    # EMBEDDING
    # =========================
    def _embed(self, texts: List[str]) -> np.ndarray:
        if self.model:
            try:
                return np.array(self.model.encode(texts, normalize_embeddings=True))
            except Exception as e:
                logger.warning(f"Embedding failed: {e}")

        # fallback (zero vectors)
        return np.zeros((len(texts), self.embedding_dim))

    # =========================
    # ADD DOCUMENT
    # =========================
    def add_document(self, doc_id: str, chunks: List[str]):
        if not chunks:
            return

        try:
            new_embeddings = self._embed(chunks)

            start_idx = len(self.chunks)

            self.chunks.extend(chunks)

            for i in range(len(chunks)):
                self.metadata.append({
                    "document_id": doc_id,
                    "chunk_index": start_idx + i
                })

            if self.embeddings is None:
                self.embeddings = new_embeddings
            else:
                self.embeddings = np.vstack([self.embeddings, new_embeddings])

            logger.info(f"✅ Added {len(chunks)} chunks for {doc_id}")

            self._save()

        except Exception as e:
            logger.exception(f"Add document failed: {e}")

    # =========================
    # SEARCH (HYBRID)
    # =========================
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        if not self.chunks:
            return []

        try:
            # ===== EMBEDDING SEARCH =====
            if self.model and self.embeddings is not None:
                query_vec = self._embed([query])[0]

                similarities = np.dot(self.embeddings, query_vec)

                top_indices = np.argsort(similarities)[::-1][:top_k]

                results = []
                for idx in top_indices:
                    results.append((
                        self.chunks[idx],
                        float(similarities[idx]),
                        self.metadata[idx]
                    ))

                return results

        except Exception as e:
            logger.warning(f"Vector search failed, fallback to keyword: {e}")

        # ===== FALLBACK KEYWORD SEARCH =====
        return self._keyword_search(query, top_k)

    # =========================
    # KEYWORD SEARCH (FALLBACK)
    # =========================
    def _keyword_search(self, query: str, top_k: int):
        query_words = set(query.lower().split())

        results = []

        for i, chunk in enumerate(self.chunks):
            chunk_words = set(chunk.lower().split())

            overlap = len(query_words & chunk_words)

            if overlap > 0:
                score = overlap / max(len(query_words), 1)

                results.append((
                    chunk,
                    min(score, 1.0),
                    self.metadata[i]
                ))

        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    # =========================
    # PERSISTENCE
    # =========================
    def _save(self):
        try:
            path = self.vectors_dir / "store.pkl"

            with open(path, "wb") as f:
                pickle.dump({
                    "chunks": self.chunks,
                    "metadata": self.metadata,
                    "embeddings": self.embeddings
                }, f)

            logger.info(f"💾 Saved vector store ({len(self.chunks)} chunks)")

        except Exception as e:
            logger.exception(f"Save failed: {e}")

    def _load(self):
        try:
            path = self.vectors_dir / "store.pkl"

            if not path.exists():
                return

            with open(path, "rb") as f:
                data = pickle.load(f)

                self.chunks = data.get("chunks", [])
                self.metadata = data.get("metadata", [])
                self.embeddings = data.get("embeddings", None)

            logger.info(f"📦 Loaded vector store ({len(self.chunks)} chunks)")

        except Exception as e:
            logger.warning(f"Load failed: {e}")

    # =========================
    # CLEAR (OPTIONAL)
    # =========================
    def clear(self):
        self.chunks = []
        self.metadata = []
        self.embeddings = None

        path = self.vectors_dir / "store.pkl"
        if path.exists():
            os.remove(path)

        logger.info("🧹 Vector store cleared")


# Singleton
vector_store = VectorStore()