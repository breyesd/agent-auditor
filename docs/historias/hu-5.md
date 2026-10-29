# HU-5: Generar informe de auditoría estructurado con citas

Como usuario, quiero recibir un informe JSON estructurado con hallazgos, severidad, sugerencias y citas de fuentes RAG.

## Especificación funcional de flujo de datos
1. Nodo `synthesize` del harness combina resultados de memoria, RAG y herramientas MCP.
2. Genera `AuditorResponse` con lista de `Finding` y `resumen` por severidad.
3. Cada hallazgo incluye cita de fuente cuando proviene de RAG.
4. Salida impresa por CLI en JSON.

## Criterios de aceptación
- [ ] Salida JSON válida contra esquema Pydantic `AuditorResponse`.
- [ ] Hallazgos con {id, tipo, severidad, archivo, linea, descripcion, sugerencia, cita_fuente}.
- [ ] Resumen con conteo por severidad (baja, media, alta, crítica).
- [ ] Citas de fuentes incluidas en hallazgos basados en RAG.

## Relación
Especificación específica: docs/especificaciones/especificacion-fase-1.md (sección 2.3).
Contratos: AuditorRequest, AuditorResponse, Finding, RagContext, McpToolResult.
