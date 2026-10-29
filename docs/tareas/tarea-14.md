# T14: Implementar nodo intent_analysis

- **id**: T14
- **título**: Implementar nodo intent_analysis
- **descripción**: Nodo que clasifica la solicitud del usuario (auditoría / refactor / cumplimiento).
- **tipo**: logica_negocio
- **tamaño**: pequena
- **dependencias**: [T12]
- **validaciones de campo**: clasificación correcta entre las tres categorías
- **librerias o métodos utilitarios**: `langchain-core`, LLM (clase base)
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: {intencion: string, confianza: float}
- **enlace a su HU**: docs/historias/hu-1.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 5)
- **estado**: [ ]
