# T7: Implementar embeddings y búsqueda semántica con umbral 0.72

- **id**: T7
- **título**: Implementar embeddings y búsqueda semántica con umbral 0.72
- **descripción**: Generar embeddings (`text-embedding-3-small` o `all-MiniLM-L6-v2`) y búsqueda semántica con corte por similitud cosínea > 0.72, formateador de contexto con citas.
- **tipo**: logica_negocio
- **tamaño**: mediana
- **dependencias**: [T5, T6]
- **validaciones de campo**: umbral cosíneo > 0.72; cada resultado incluye cita de fuente
- **librerias o métodos utilitarios**: `sentence-transformers`, `chromadb`/`qdrant-client`
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: {documentos: [], puntuaciones: [], citas: []}
- **enlace a su HU**: docs/historias/hu-3.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 2)
- **estado**: [ ]
