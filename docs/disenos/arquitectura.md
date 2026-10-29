# Análisis Arquitectónico — DSIA

## Stack detectado
proyecto.stack = `python/langgraph` (inferido de la especificación general: Python 3.11+, LangGraph, ChromaDB/Qdrant, Pydantic v2, DeepEval/Ragas, MCP SDK).

## Decisiones de arquitectura

El sistema es un monorepo distribuido en 5 componentes independientes comunicados por contratos estrictos:

| Subproyecto | Módulo | Responsabilidad | Tecnología clave |
|---|---|---|---|
| 1 | `modules/mcp_server` | Servidor de herramientas desacoplado (FS + git) | `mcp` SDK, stdio |
| 2 | `modules/rag_engine` | Motor RAG: chunking, embeddings, vector store, retrieval | ChromaDB/Qdrant embebido, sentence-transformers |
| 3 | `modules/memory_store` | Memoria híbrida (episódica + semántica) | sqlite3 + almacén KV/vectorial |
| 4 | `modules/evals_suite` | Suite de evaluación con golden dataset | DeepEval/Ragas, pytest |
| 5 | `modules/agent_harness` | Orquestador y harness (LangGraph StateMachine) | LangGraph, langchain-core, OpenTelemetry |

## Flujo de datos

```
Usuario/CLI → agent_harness (runtime StateMachine)
   ├─→ mcp_server (get_git_diff, read_source_file, run_static_analysis)
   ├─→ memory_store (checkpoints + perfiles semánticos)
   ├─→ rag_engine (retrieval semántico con citas)
   └─→ evals_suite (gate de calidad CI/CD)
```

## Contratos entre componentes
- Todos los componentes expuestos vía interfaces tipadas con Pydantic v2.
- Comunicación por contratos estrictos (JSON schema validado).
- El harness coordina reintentos, guardrails (máx. 6 iteraciones) y observabilidad (OpenTelemetry/Langfuse).

## Guardrails y resiliencia
- Límite de 6 iteraciones en bucles de razonamiento.
- Validación de respuestas con Pydantic; fallback determinista ante error.
- Timeouts por herramienta MCP.
