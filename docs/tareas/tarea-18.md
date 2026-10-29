# T18: Implementar nodo validate con evals_suite

- **id**: T18
- **título**: Implementar nodo validate con evals_suite
- **descripción**: Nodo de gate de calidad que valida el informe generado (faithfulness, precisión de herramientas, validez de esquema Pydantic) antes de entregarlo.
- **tipo**: pruebas
- **tamaño**: mediana
- **dependencias**: [T10]
- **validaciones de campo**: JSON Schema Validity pasa sin fallback; Tool Selection Accuracy verificada
- **librerias o métodos utilitarios**: `deepeval` o `ragas`, `pydantic v2`
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: resultado de validación {aprobado, metricas, detalle}
- **enlace a su HU**: docs/historias/hu-6.md, docs/historias/hu-1.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 4, 5)
- **estado**: [ ]
