# HU-1: Enviar código/diff para auditoría completa

Como desarrollador, quiero enviar un archivo o diff staged al agente auditor para obtener un informe de hallazgos de seguridad, cumplimiento y estilo con sugerencias de refactorización.

## Especificación funcional de flujo de datos
1. Usuario invoca el CLI con ruta de archivo o diff.
2. `agent_harness` nodo `input`: normaliza entrada y valida esquema `AuditorRequest` (Pydantic).
3. Nodo `intent_analysis`: clasifica la solicitud (auditoría / refactor / cumplimiento).
4. Nodo `memory_consult`: lee perfil y reglas aprobadas de `memory_store`.
5. Nodo `rag_retrieve`: recupera directrices de `rag_engine` con umbral cosíneo > 0.72 y citas.
6. Nodo `mcp_execute`: ejecuta herramientas de `mcp_server` (get_git_diff, read_source_file, run_static_analysis).
7. Nodo `synthesize`: genera `AuditorResponse` con hallazgos, severidad y sugerencias.
8. Nodo `validate`: `evals_suite` valida schema y faithfulness.
9. CLI imprime informe JSON estructurado al usuario.

## Criterios de aceptación
- [ ] Entrada de archivo o diff aceptada y validada con Pydantic.
- [ ] Informe incluye hallazgos con {id, tipo, severidad, archivo, linea, descripcion, sugerencia, cita_fuente}.
- [ ] Resumen con conteo por severidad.
- [ ] Métricas de latencia, tokens y herramientas invocadas.
- [ ] Tiempo de respuesta < 5 s para un archivo.
- [ ] Fallo de herramienta MCP no bloquea el informe (fallback determinista).

## Relación
Especificación específica: docs/especificaciones/especificacion-fase-1.md (sección 2.2, 2.3, 3, 4).
