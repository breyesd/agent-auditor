# T11: Implementar nodo synthesize del harness

- **id**: T11
- **título**: Implementar nodo synthesize del harness
- **descripción**: Nodo `synthesize` de LangGraph que combina resultados de memoria, RAG y herramientas MCP en `AuditorResponse` con hallazgos, severidad y sugerencias.
- **tipo**: logica_negocio
- **tamaño**: mediana
- **dependencias**: [T2, T3, T4, T5, T6, T7, T8, T9, T10]
- **validaciones de campo**: salida valida contra `AuditorResponse`; hallazgos con cita_fuente cuando provienen de RAG
- **librerias o métodos utilitarios**: `langgraph`, `pydantic v2`
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: `AuditorResponse` con lista de `Finding` y `resumen`
- **enlace a su HU**: docs/historias/hu-5.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 5)
- **estado**: [ ]
