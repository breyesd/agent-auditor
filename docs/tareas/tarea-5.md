# T5: Configurar vector store ChromaDB/Qdrant embebido

- **id**: T5
- **título**: Configurar vector store ChromaDB/Qdrant embebido
- **descripción**: Levantar almacén vectorial embebido para el motor RAG (`modules/rag_engine`).
- **tipo**: base_de_datos
- **tamaño**: mediana
- **dependencias**: []
- **validaciones de campo**: almacén inicia y acepta inserción/consulta de vectores
- **librerias o métodos utilitarios**: `chromadb` o `qdrant-client`, `sentence-transformers`
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: colección de {id, vector, metadata, documento}
- **enlace a su HU**: docs/historias/hu-3.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 2)
- **estado**: [ ]
