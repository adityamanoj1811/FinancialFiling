"""
vector_store.py
----------------
Handles embedding text chunks and indexing them in a FAISS vector index
with normalized inner product (cosine similarity) and metadata attribution.
Provides source filtering, document stats, chunk browsing, and document deletion.
"""

import faiss
import numpy as np
from fastembed import TextEmbedding
from backend.config import EMBEDDING_MODEL_NAME, TOP_K_PER_DOCUMENT


class VectorStore:
    """
    Wraps a FAISS index, fastembed ONNX embedding engine, and chunk metadata store.
    """

    def __init__(self):
        # Load local ONNX embedding model (runs fast on CPU)
        self.embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL_NAME)

        # Discover embedding dimensionality dynamically
        dummy_vector = next(self.embedding_model.embed(["dimension probe"]))
        self.embedding_dim = len(dummy_vector)

        # IndexFlatIP with normalized vectors = exact cosine similarity
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.metadata = []

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        """L2-normalize vectors so inner product == cosine similarity."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        return vectors / norms

    def add_chunks(self, chunks: list[dict]):
        """
        Embed a list of text chunks and add them to the FAISS index.
        """
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        raw_vectors = np.array(list(self.embedding_model.embed(texts)), dtype="float32")
        normalized_vectors = self._normalize(raw_vectors)

        self.index.add(normalized_vectors)
        self.metadata.extend(chunks)

    def search(self, query: str, top_k: int = TOP_K_PER_DOCUMENT, source_filter: str = None) -> list[dict]:
        """
        Retrieve the top_k most semantically similar chunks for a query.
        """
        if self.index.ntotal == 0 or not query.strip():
            return []

        query_vector = np.array(list(self.embedding_model.embed([query])), dtype="float32")
        query_vector = self._normalize(query_vector)

        # Over-fetch if filtering by source
        fetch_k = top_k * 5 if source_filter else top_k
        fetch_k = min(fetch_k, self.index.ntotal)

        similarity_scores, indices = self.index.search(query_vector, fetch_k)

        results = []
        for score, idx in zip(similarity_scores[0], indices[0]):
            if idx == -1 or idx >= len(self.metadata):
                continue
            chunk = dict(self.metadata[idx])
            if source_filter and chunk["source"] != source_filter:
                continue
            chunk["score"] = float(score)
            results.append(chunk)
            if len(results) >= top_k:
                break

        return results

    def get_all_sources(self) -> list[str]:
        """Return the unique list of document names currently indexed."""
        return sorted(set(chunk["source"] for chunk in self.metadata))

    def get_source_stats(self) -> dict:
        """
        Calculate summary statistics for all indexed documents.
        """
        stats = {}
        for chunk in self.metadata:
            source = chunk["source"]
            if source not in stats:
                stats[source] = {
                    "chunks": 0,
                    "pages": set(),
                    "total_chars": 0,
                    "est_tokens": 0,
                }
            stats[source]["chunks"] += 1
            stats[source]["pages"].add(chunk.get("page_number", 1))
            stats[source]["total_chars"] += chunk.get("char_count", len(chunk["text"]))
            stats[source]["est_tokens"] += chunk.get("token_est", len(chunk["text"]) // 4)

        result = {}
        for source, s in stats.items():
            result[source] = {
                "chunk_count": s["chunks"],
                "page_count": len(s["pages"]),
                "pages_list": sorted(s["pages"]),
                "total_chars": s["total_chars"],
                "est_tokens": s["est_tokens"],
            }
        return result

    def get_all_chunks(self, source_filter: str = None) -> list[dict]:
        """Return all metadata chunks, optionally filtered by source."""
        if source_filter:
            return [c for c in self.metadata if c["source"] == source_filter]
        return list(self.metadata)

    def remove_source(self, source_name: str):
        """
        Remove a document and rebuild the FAISS index with remaining chunks.
        """
        remaining_chunks = [c for c in self.metadata if c["source"] != source_name]
        self.clear()
        if remaining_chunks:
            self.add_chunks(remaining_chunks)

    def clear(self):
        """Reset the vector store and FAISS index."""
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.metadata = []
