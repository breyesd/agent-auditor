# DevSecOps Intelligent Auditor (DSIA)

Agente de IA modular y auditable para revisiones de código, validación de cumplimiento de estándares de seguridad y sugerencias de refactorización. Construido como un monorepo distribuido en 5 componentes independientes comunicados por contratos estrictos.

## Arquitectura de Alto Nivel

```
Usuario/CLI → agent_harness (runtime StateMachine)
   ├─→ mcp_server (get_git_diff, read_source_file, run_static_analysis)
   ├─→ memory_store (checkpoints + perfiles semánticos)
   ├─→ rag_engine (retrieval semántico con citas)
   └─→ evals_suite (gate de calidad CI/CD)
```

### 5 Subproyectos

| Subproyecto | Módulo | Responsabilidad |
|---|---|---|
| 1 | `modules/mcp_server` | Servidor de herramientas (FS + git) vía stdio |
| 2 | `modules/rag_engine` | Motor RAG: chunking, embeddings, vector store |
| 3 | `modules/memory_store` | Memoria híbrida (episódica + semántica) |
| 4 | `modules/evals_suite` | Suite de evaluación (DeepEval/Ragas) |
| 5 | `modules/agent_harness` | Orquestador LangGraph + CLI |

## Requisitos

- Python 3.11+
- Dependencias declaradas en `pyproject.toml`

## Instalación

```bash
# Crear entorno virtual (opcional pero recomendado)
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -e .
```

## Uso

### CLI de auditoría

```bash
# Auditar un archivo
python3 -m src.modules.agent_harness.cli auditar src/mi_archivo.py

# Auditar un diff
python3 -m src.modules.agent_harness.cli auditar --diff "diff --git a/file.py b/file.py ..."

# Salida en JSON
python3 -m src.modules.agent_harness.cli auditar src/archivo.py --json

# Con reglas personalizadas y exclusiones
python3 -m src.modules.agent_harness.cli auditar src/archivo.py --reglas "no-print" --exclusiones "no-unused-in-tests"
```

### Servidor MCP

```bash
python3 -m src.modules.agent_harness.cli servidor-mcp
```

## Pruebas

```bash
# Ejecutar todas las pruebas
python3 -m pytest tests/

# Con cobertura
python3 -m pytest tests/ --cov=src/modules --cov-report=term
```

## Contratos (Pydantic v2)

Todos los componentes se comunican mediante esquemas JSON estrictos:

- `AuditorRequest` — solicitud de entrada (archivo, diff, reglas)
- `AuditorResponse` — informe de auditoría (hallazgos, resumen, métricas)
- `Finding` — hallazgo individual (tipo, severidad, archivo, línea, descripción, sugerencia, cita)
- `RagContext` — contexto recuperado del motor RAG
- `McpToolResult` — resultado de herramienta MCP

## Flujo de Desarrollo (Flujo Ágil)

El proyecto sigue el flujo ágil modular con 11 etapas:

1. Especificación general ✅
2. Análisis arquitectónico ✅
3. Especificaciones específicas ✅
4. Historias de usuario (HU-1 a HU-6) ✅
5. Tareas (T1 a T21) ✅
6. Implementación de código fuente ✅
7. Pruebas unitarias (85% cobertura) ✅
8. Pruebas de integración/sistema ✅
9. Revisión de código/docs ✅
10. Despliegue (pendiente)
11. Commits (pendiente)

## Documentación del Proyecto

| Archivo | Descripción |
|---|---|
| `docs/especificaciones/especificaion-inicial-proyecto.md` | Especificación general (DSIA) |
| `docs/disenos/arquitectura.md` | Análisis arquitectónico y stack |
| `docs/especificaciones/especificacion-fase-1.md` | Especificaciones de la fase 1 |
| `docs/historias/hu-*.md` | Historias de usuario |
| `docs/tareas/tarea-*.md` | Tareas de implementación |
| `docs/revision/reporte-revision-etapa-9.md` | Reporte de revisión de código y seguridad |
| `docs/skill-config.yaml` | Configuración del flujo ágil |
