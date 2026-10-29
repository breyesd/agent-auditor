# Especificaciones Específicas — DSIA (Fase 1)

Fase: subconjunto inicial de funcionalidades del agente auditor.

## 1. Alcance de la fase

Cubrir el flujo completo de datos de una solicitud de auditoría de código:

1. Usuario envía código/diff al CLI.
2. `agent_harness` recibe la entrada y activa la StateMachine.
3. Se consultan `memory_store` (perfil/reglas aprobadas) y `rag_engine` (directrices de seguridad/estilo).
4. Se ejecutan herramientas de `mcp_server` (get_git_diff, read_source_file, run_static_analysis).
5. Se sintetiza el informe de auditoría con citas de fuentes.
6. `evals_suite` valida la calidad (faithfulness, tool accuracy, schema validity).

## 2. Especificaciones funcionales

### 2.1. Entrada del usuario
- Ruta de archivo o diff staged.
- Opcional: reglas personalizadas o exclusiones.

### 2.2. Nodos del harness (LangGraph)
- `input`: normaliza entrada y valida esquema Pydantic.
- `intent_analysis`: clasifica tipo de solicitud (auditoría, refactor, cumplimiento).
- `memory_consult`: lee perfil de usuario y reglas aprobadas de `memory_store`.
- `rag_retrieve`: recupera directrices con umbral cosíneo > 0.72 y citas.
- `mcp_execute`: ejecuta herramientas MCP necesarias.
- `synthesize`: genera informe estructurado con hallazgos, severidad y sugerencias.
- `validate`: gate de calidad con `evals_suite` (schema + faithfulness).

### 2.3. Salida del informe
JSON estructurado con:
- `hallazgos`: lista de {id, tipo, severidad, archivo, linea, descripcion, sugerencia, cita_fuente}.
- `resumen`: conteo por severidad.
- `metricas`: latencia, tokens, herramientas invocadas.

## 3. Casos de borde
- Archivo vacío o sin cambios → informe vacío válido.
- Diff inválido → error controlado con mensaje descriptivo.
- Umbral de similitud no alcanzado → informe sin citas RAG, marcado como tal.
- Fallo de herramienta MCP → fallback determinista, continuar con las demás.

## 4. Requisitos no funcionales
- Tiempos de respuesta < 5 s para auditoría de un archivo.
- Validación Pydantic en todas las respuestas estructuradas.
- Observabilidad: spans OpenTelemetry por nodo del grafo.
- Máx. 6 iteraciones de razonamiento por solicitud.

## 5. Contratos entre componentes (Pydantic)
- `AuditorRequest`, `AuditorResponse`, `Finding`, `RagContext`, `McpToolResult`.
- Comunicación JSON estricta entre subproyectos.
