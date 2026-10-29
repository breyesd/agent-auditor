# T20: Implementar métricas faithfulness, tool accuracy, schema validity

- **id**: T20
- **título**: Implementar métricas faithfulness, tool accuracy, schema validity
- **descripción**: Implementar métricas de evaluación: Faithfulness, Context Precision/Recall, Tool Selection Accuracy, JSON Schema Validity.
- **tipo**: pruebas
- **tamaño**: mediana
- **dependencias**: [T10, T19]
- **validaciones de campo**: cada métrica retorna puntuación interpretable; gate falla si umbral no alcanzado
- **librerias o métodos utilitarios**: `deepeval` o `ragas`, `pytest`
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: {faithfulness, context_precision, context_recall, tool_accuracy, schema_valid}
- **enlace a su HU**: docs/historias/hu-6.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 4)
- **estado**: [ ]
