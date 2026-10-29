# HU-3: Recuperar directrices de seguridad y estilo vía RAG

Como auditor, quiero que el agente fundamente sus recomendaciones en directrices de arquitectura, OWASP Top 10 y guías de estilo indexadas, con citas explícitas de fuentes.

## Especificación funcional de flujo de datos
1. `rag_engine` indexa normativas (chunking semántico/markdown-aware, 512 tokens, 10% overlap).
2. Embeddings: `text-embedding-3-small` o `all-MiniLM-L6-v2`.
3. Almacenamiento: ChromaDB o Qdrant embebido.
4. Consulta: búsqueda semántica con umbral cosíneo > 0.72.
5. Formateador de contexto devuelve citas explícitas de fuentes.

## Criterios de aceptación
- [ ] Chunking 512 tokens con 10% overlap.
- [ ] Umbral de similitud cosínea > 0.72 para corte.
- [ ] Cada recomendación incluye cita explícita de fuente.
- [ ] Si no se alcanza umbral, informe marcado como sin citas RAG.

## Relación
Especificación específica: docs/especificaciones/especificacion-fase-1.md (sección 2.2 nodo rag_retrieve, 3 casos de borde).
Subproyecto 2: modules/rag_engine.
