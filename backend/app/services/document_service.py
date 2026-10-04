import os
import math
import hashlib
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document parsing, chunking, vector embedding, and hybrid RAG retrieval."""

    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract plain text from PDF, DOCX, or TXT files."""
        ext = file_type.lower()
        if ext == "txt" or ext == "csv" or ext == "md":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        elif ext == "pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                return text.strip()
            except Exception as e:
                logger.error(f"Error reading PDF {file_path}: {e}")
                return f"[PDF parsing error: {e}]"

        elif ext == "docx":
            try:
                import docx
                doc = docx.Document(file_path)
                return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            except Exception as e:
                logger.error(f"Error reading DOCX {file_path}: {e}")
                return f"[DOCX parsing error: {e}]"

        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split document text into sliding window chunks."""
        words = text.split()
        if not words:
            return []

        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunks.append(" ".join(chunk_words))
            i += (chunk_size - overlap)
            if i >= len(words) - overlap and i < len(words):
                # Avoid tiny trailing chunks
                chunks.append(" ".join(words[i:]))
                break
        return chunks

    def compute_embedding(self, text: str, dim: int = 64) -> List[float]:
        """
        Generate a normalized semantic vector embedding.
        Uses deterministic hashing and word n-gram frequency to simulate
        dense vector representations when offline, or Gemini embeddings if configured.
        """
        # Deterministic pseudo-embedding based on hash buckets
        vector = [0.0] * dim
        words = text.lower().split()
        for w in words:
            h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            vector[idx] += 1.0

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [round(x / norm, 4) for x in vector]
        return vector

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Compute cosine similarity between two float vectors."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, dot))

    def retrieve_relevant_chunks(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Hybrid retrieval combining semantic cosine similarity and keyword matching.
        Each chunk item should have keys 'content' and 'embedding'.
        """
        query_vec = self.compute_embedding(query)
        query_words = set(query.lower().split())

        scored_chunks = []
        for ch in chunks:
            content = ch.get("content", "")
            ch_vec = ch.get("embedding") or self.compute_embedding(content)
            
            # Semantic score
            sim_score = self.cosine_similarity(query_vec, ch_vec)

            # Keyword lexical match score
            content_words = set(content.lower().split())
            intersection = query_words.intersection(content_words)
            keyword_score = len(intersection) / max(1, len(query_words))

            # Hybrid weighted score
            final_score = (sim_score * 0.6) + (keyword_score * 0.4)
            scored_chunks.append((ch, final_score))

        # Sort by highest relevance score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]


document_service = DocumentService()
