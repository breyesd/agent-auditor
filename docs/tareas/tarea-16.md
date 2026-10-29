# T16: Implementar nodo rag_retrieve

- **id**: T16
- **título**: Implementar nodo rag_retrieve
- **descripción**: Nodo que recupera directrices de `rag_engine` con umbral cosíneo > 0.72 y citas explícitas de fuentes.
- **tipo**: logica_negocio
- **tamaño**: pequena
- **dependencias**: [T5, T6, T7]
- **validaciones de campo**: umbral > 0.72; resultados incluyen cita de fuente
- **librerias o métodos utilitarios**: `chromadb`/`qdrant-client`, `sentence-transformers`
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: `RagContext` con documentos y citas
- **enlace a su HU**: docs/historias/hu-3.md, docs/historias/hu-1.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 2, 5)
- **estado**: [ ]
