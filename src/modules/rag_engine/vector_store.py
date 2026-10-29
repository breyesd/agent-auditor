"""Vector store embebido para el motor RAG (Subproyecto 2).

Soporta ChromaDB o Qdrant en modo embebido. Configuración por variable
de entorno DSIA_VECTOR_STORE (chromadb | qdrant).
"""

from __future__ import annotations

import os
from typing import Any


class VectorStoreConfig:
    """Configuración del almacén vectorial."""

    def __init__(self) -> None:
        self.provider = os.getenv("DSIA_VECTOR_STORE", "chromadb").lower()
        self.persist_dir = os.getenv("DSIA_VECTOR_PERSIST_DIR", "./data/chromadb")
        self.collection_name = os.getenv("DSIA_VECTOR_COLLECTION", "dsia_directrices")
        self.embedding_model = os.getenv(
            "DSIA_EMBEDDING_MODEL", "all-MiniLM-L6-v2"
        )
        self.similarity_threshold = float(
            os.getenv("DSIA_SIMILARITY_THRESHOLD", "0.72")
        )


class VectorStore:
    """Interfaz sobre el almacén vectorial embebido."""

    def __init__(self, config: VectorStoreConfig | None = None) -> None:
        self.config = config or VectorStoreConfig()
        self._client = None
        self._collection = None
        self._initialized = False

    def _ensure_client(self) -> None:
        if self._initialized:
            return
        if self.config.provider == "chromadb":
            try:
                import chromadb  # type: ignore

                self._client = chromadb.PersistentClient(
                    path=self.config.persist_dir
                )
                self._collection = self._client.get_or_create_collection(
                    name=self.config.collection_name
                )
            except ImportError as exc:
                raise RuntimeError("chromadb no está instalado") from exc
        elif self.config.provider == "qdrant":
            try:
                from qdrant_client import QdrantClient  # type: ignore

                self._client = QdrantClient(path=self.config.persist_dir)
                self._collection = self.config.collection_name
            except ImportError as exc:
                raise RuntimeError("qdrant-client no está instalado") from exc
        else:
            raise ValueError(f"Proveedor de vector store no soportado: {self.config.provider}")
        self._initialized = True

    def add_texts(
        self, texts: list[str], metadatas: list[dict[str, Any]] | None = None
    ) -> list[str]:
        """Añade textos al almacén vectorial. Retorna los IDs asignados."""
        self._ensure_client()
        if self.config.provider == "chromadb":
            metadatas = metadatas or [{}] * len(texts)
            ids = [f"doc-{i}" for i in range(len(texts))]
            self._collection.add(documents=texts, metadatas=metadatas, ids=ids)  # type: ignore[attr-defined]
            return ids
        # Qdrant path (embeddings would be computed upstream)
        raise NotImplementedError("Qdrant add_texts no implementado en esta versión")

    def query(
        self, text: str, n_results: int = 5
    ) -> dict[str, list[Any]]:
        """Consulta semántica. Retorna documentos, puntuaciones y metadatas."""
        self._ensure_client()
        if self.config.provider == "chromadb":
            results = self._collection.query(  # type: ignore[attr-defined]
                query_texts=[text], n_results=n_results
            )
            return {
                "documentos": results.get("documents", [[]])[0],
                "puntuaciones": results.get("distances", [[]])[0],
                "metadatas": results.get("metadatas", [[]])[0],
            }
        raise NotImplementedError("Qdrant query no implementado en esta versión")
