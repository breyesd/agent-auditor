# HU-6: Validar calidad del informe con evals_suite

Como ingeniero de calidad, quiero que cada informe pase un gate de evaluación (faithfulness, precisión de herramientas, validez de esquema) antes de entregarse al usuario.

## Especificación funcional de flujo de datos
1. Nodo `validate` invoca `evals_suite` sobre el informe generado.
2. Métricas: Faithfulness, Context Precision/Recall, Tool Selection Accuracy, JSON Schema Validity.
3. Dataset de prueba: golden_dataset.json con 30 casos (código vulnerable, preguntas de estándares, conflictos).
4. Si el gate falla, se aplica fallback determinista y se marca el informe.

## Criterios de aceptación
- [ ] Faithfulness: análisis basado estrictamente en documentación RAG recuperada.
- [ ] Tool Selection Accuracy: agente invoca herramienta MCP adecuada.
- [ ] JSON Schema Validity: respuesta pasa validación Pydantic sin fallback de error.
- [ ] golden_dataset.json con 30 casos de prueba.
- [ ] Dependencias: deepeval o ragas, pytest.

## Relación
Especificación específica: docs/especificaciones/especificacion-fase-1.md (sección 2.2 nodo validate, 4 no funcionales).
Subproyecto 4: modules/evals_suite.
