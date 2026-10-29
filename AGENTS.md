# agent-auditor — AGENTS.md

## Propósito del proyecto

DevSecOps Intelligent Auditor (DSIA) es un agente de IA modular y auditable para revisiones de código, validación de cumplimiento de estándares de seguridad y sugerencias de refactorización. Funciona como un monorepo distribuido en 5 componentes independientes comunicados por contratos estrictos (Pydantic v2).

## Stack

- Python 3.11+
- LangGraph, langchain-core
- ChromaDB / Qdrant (vector store embebido)
- sentence-transformers / langchain-text-splitters
- Pydantic v2
- mcp SDK oficial (transporte stdio)
- DeepEval / Ragas (evals), pytest
- typer (CLI), OpenTelemetry / Langfuse (observabilidad)

## Estructura del repositorio

```
agent-auditor/
├── pyproject.toml            # dependencias y metadatos del proyecto
├── README.md                 # guía de inicio, arquitectura, uso del CLI
├── docs/                     # artefactos del flujo ágil
│   ├── skill-config.yaml     # configuración del flujo (modelos, puertas, artefactos)
│   ├── plantillas/           # templates de cada etapa del flujo ágil
│   ├── especificaciones/     # especificación general + específicas por fase
│   ├── historias/            # HU-1 a HU-6
│   ├── tareas/               # T1 a T21 con dependencias y checkbox
│   ├── disenos/              # arquitectura.md
│   └── revision/             # reporte de revisión de código y seguridad
├── src/modules/              # código fuente (5 subproyectos)
│   ├── mcp_server/           # Subproyecto 1: servidor MCP (get_git_diff, read_source_file, run_static_analysis)
│   ├── rag_engine/           # Subproyecto 2: vector store, chunking, retriever
│   ├── memory_store/         # Subproyecto 3: checkpoints sqlite3, perfil store, extractor de hechos
│   ├── evals_suite/          # Subproyecto 4: golden_dataset.json, suite de evaluación
│   └── agent_harness/        # Subproyecto 5: contratos, nodos, state machine, CLI, observabilidad
└── tests/                    # pruebas unitarias, de cobertura e integración
    ├── test_dsia.py
    ├── test_cobertura_adicional.py
    └── test_integracion.py
```

## Comandos de desarrollo

```bash
# Instalar dependencias
pip install -e .

# Ejecutar pruebas (unidad + integración + cobertura)
python3 -m pytest tests/ --cov=src/modules --cov-report=term

# Solo pruebas unitarias
python3 -m pytest tests/test_dsia.py tests/test_cobertura_adicional.py

# Solo pruebas de integración
python3 -m pytest tests/test_integracion.py

# Linting
python3 -m ruff check src/ tests/

# Type checking (MyPy; nota: stubs faltantes para mcp/langgraph/chromadb)
python3 -m mypy src/modules/

# Ejecutar el servidor MCP
python3 -m src.modules.agent_harness.cli servidor-mcp

# Ejecutar auditoría por CLI
python3 -m src.modules.agent_harness.cli auditar <archivo> [--diff "..."] [--json]
```

## Convenciones de código

- Lenguaje: Python 3.11+, tipado estático con `typing` / `collections.abc`
- Contratos entre componentes: esquemas Pydantic v2 en `src/modules/agent_harness/contracts.py`
- Docstrings en todos los módulos y funciones públicas
- Sin comentarios en línea salvo los necesarios (regla del proyecto: NO añadir comentarios a menos que se pida)
- Manejo de excepciones con fallback determinista (no capturar `Exception` ciegamente)
- Linter configurado: `ruff` (reglas por defecto + I, UP, DTZ, TRY, BLE, PLW)
- Máximo 6 iteraciones en el bucle de razonamiento del harness (guardrail)

## Flujo de trabajo

El proyecto sigue 11 etapas con puertas de bloqueo entre etapas:

1. Especificación general
2. Análisis arquitectónico
3. Especificaciones específicas
4. Historias de usuario
5. Tareas
6. Implementación de código fuente
7. Pruebas unitarias (cobertura objetivo ≥80%, actual 85%)
8. Pruebas de integración/sistema
9. Revisión de código/docs (seguridad OWASP, linting, typechecking, documentación)
10. Despliegue
11. Commits

Cada etapa tiene su artefacto bajo `docs/`. Antes de avanzar de etapa se requiere aprobación explícita.

## Subproyectos y responsabilidades

| Subproyecto | Módulo | Responsabilidad clave |
|---|---|---|
| 1 | `mcp_server` | Utilidades locales FS + git vía stdio |
| 2 | `rag_engine` | Chunking, embeddings, búsqueda semántica con citas |
| 3 | `memory_store` | Checkpoints (sqlite3) + perfiles semánticos de usuario |
| 4 | `evals_suite` | golden_dataset.json (30 casos), métricas faithfulness/tool-accuracy/schema |
| 5 | `agent_harness` | StateMachine LangGraph, nodos, CLI, observabilidad OpenTelemetry |

## Flujo de datos de una auditoría (HU-1)

1. CLI recibe archivo o diff → `AuditorRequest` (Pydantic)
2. `NodoInput`: normaliza y valida entrada
3. `NodoIntentAnalysis`: clasifica intención (auditoría / refactor / cumplimiento)
4. `NodoMemoryConsult`: lee perfil y reglas aprobadas de `memory_store`
5. `NodoRagRetrieve`: recupera directrices de `rag_engine` (umbral cosíneo > 0.72 + citas)
6. `NodoMcpExecute`: ejecuta herramientas de `mcp_server` con fallback determinista
7. `NodoSynthesize`: genera `AuditorResponse` con hallazgos y resumen
8. `NodoValidate`: gate de calidad con `evals_suite` (schema + faithfulness)
9. CLI imprime informe JSON estructurado

## Cómo contribuir / preparar un cambio

1. Verificar que exista el artefacto de la etapa previa en `docs/`
2. Implementar la tarea correspondiente bajo `src/modules/` o `tests/`
3. Ejecutar `ruff check src/ tests/` y `pytest tests/` antes de commitear
4. Actualizar documentación en `docs/` si cambia el alcance
5. Commit con mensaje descriptivo (estilo: `feat: ...`, `fix: ...`, `docs: ...`, `test: ...`)

## Archivos generados / a ignorar

- `.venv/`, `.coverage`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `data/`
- Archivos accidentales `=*.*.*` (salida mal redirigida de pip) — no versionar
