from dataclasses import dataclass

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.retrieval.chunker import DocumentChunk


@dataclass
class RetrievalResult:
    chunk: DocumentChunk
    score: float


class MedicalRecordRetriever:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(model_name)

        self.index = None
        self.chunks: list[DocumentChunk] = []

    def build_index(
        self,
        chunks: list[DocumentChunk],
    ) -> None:

        if not chunks:
            raise ValueError("Cannot build index with no chunks.")

        self.chunks = chunks

        texts = [chunk.text for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[RetrievalResult]:

        if self.index is None:
            raise RuntimeError(
                "Index has not been built. "
                "Call build_index() first."
            )

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        k = top_k or settings.top_k
        k = min(k, len(self.chunks))

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32",
        )

        scores, indices = self.index.search(
            query_embedding,
            k,
        )

        results: list[RetrievalResult] = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index == -1:
                continue

            results.append(
                RetrievalResult(
                    chunk=self.chunks[index],
                    score=float(score),
                )
            )

        return results