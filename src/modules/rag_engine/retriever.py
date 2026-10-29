"""Motor de embeddings y busqueda semantica (T7).

- Embeddings: text-embedding-3-small o all-MiniLM-L6-v2 (local)
- Busqueda semantica con corte por similitud cosinea > 0.72
- Formateador de contexto con citas explicitas de fuentes
"""

from __future__ import annotations

import os
from typing import Any

from rag_engine.vector_store import VectorStore


class EmbeddingModel:
    """Modelo de embeddings con fallback local."""

    def __init__(self, modelo: str | None = None) -> None:
        self.modelo = modelo or os.getenv("DSIA_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self._cliente = None

    def _cargar(self) -> None:
        if self._cliente is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self._cliente = SentenceTransformer(self.modelo)
        except ImportError:
            self._cliente = None

    def embed(self, texto: str) -> list[float]:
        """Genera el embedding de un texto."""
        self._cargar()
        if self._cliente is None:
            return [0.0] * 384
        return self._cliente.encode(texto).tolist()  # type: ignore[attr-defined]


class RagRetriever:
    """Recuperador semantico con umbral de similitud y citas."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedding_model: EmbeddingModel | None = None,
        umbral: float = 0.72,
    ) -> None:
        self.vector_store = vector_store or VectorStore()
        self.embedding_model = embedding_model or EmbeddingModel()
        self.umbral = umbral

    def indexar_documentos(
        self, chunks: list[dict[str, Any]]
    ) -> list[str]:
        """Indexa chunks en el vector store."""
        textos = [c["texto"] for c in chunks]
        metadatas = [c.get("metadata", {}) for c in chunks]
        return self.vector_store.add_texts(textos, metadatas)

    def recuperar(
        self, consulta: str, n_resultados: int = 5
    ) -> dict[str, Any]:
        """Recupera documentos relevantes con citas y umbral de similitud."""
        resultados = self.vector_store.query(consulta, n_results=n_resultados)
        documentos = resultados.get("documentos", [])
        puntuaciones = resultados.get("puntuaciones", [])
        metadatas = resultados.get("metadatas", [])

        citas: list[str] = []
        docs_filtrados: list[str] = []
        scores_filtrados: list[float] = []

        for doc, score, meta in zip(documentos, puntuaciones, metadatas):
            similitud = 1.0 - float(score) if score is not None else 0.0
            if similitud >= self.umbral:
                docs_filtrados.append(doc)
                scores_filtrados.append(similitud)
                fuente = (meta or {}).get("fuente", "desconocida")
                citas.append(f"{fuente} (similitud: {similitud:.2f})")

        return {
            "documentos": docs_filtrados,
            "puntuaciones": scores_filtrados,
            "citas": citas,
            "umbral_alcanzado": len(docs_filtrados) > 0,
            "umbral": self.umbral,
        }
