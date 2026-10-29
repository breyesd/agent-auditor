"""Pipeline de chunking semántico/markdown-aware (T6).

Chunking de normativas de arquitectura y guías de estilo:
- tamaño 512 tokens, 10% overlap
- respeta límites de markdown
"""

from __future__ import annotations

from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingPipeline:
    """Divide documentos en chunks semánticos con overlap."""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 51,  # 10% de 512
        separadores: list[str] | None = None,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separadores = separadores or [
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            " ",
            "",
        ]
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.separadores,
            length_function=len,
        )

    def chunk_documento(
        self, texto: str, metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Divide un documento en chunks con metadatas asociadas."""
        metadata = metadata or {}
        documentos = self._splitter.create_documents([texto], metadatas=[metadata])
        return [
            {
                "texto": doc.page_content,
                "metadata": doc.metadata,
                "token_count": len(doc.page_content),
            }
            for doc in documentos
        ]

    def chunk_archivos(
        self, ruta_archivo: str, metadata_base: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Lee un archivo y lo divide en chunks."""
        from pathlib import Path

        path = Path(ruta_archivo)
        texto = path.read_text(encoding="utf-8")
        metadata = metadata_base or {}
        metadata["fuente"] = str(path)
        return self.chunk_documento(texto, metadata)
