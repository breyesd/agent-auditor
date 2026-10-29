**DevSecOps Intelligent Auditor (DSIA)**, integrando los 5 pilares de ingeniería de IA.

---

# Especificación Técnica: DevSecOps Intelligent Auditor (DSIA)

## 1. Visión y Objetivos del Sistema

Construir un agente de IA modular y auditable capaz de realizar revisiones de código, validar cumplimiento de estándares de seguridad y sugerir refactorizaciones fundamentadas en directrices técnicas. El proyecto funciona como un monorepo distribuido en 5 componentes independientes comunicados por contratos estrictos.

* **Objetivo de Ingeniería:** Aprender la implementación práctica de protocolos abiertos (MCP), técnicas de recuperación semántica (RAG), almacenamiento contextual de estados (Memoria), baterías de pruebas cuantitativas (Evals) y bucles de ejecución resilientes (Harness).
* **Stack Principal:** Python 3.11+, LangGraph, ChromaDB/Qdrant, Pydantic v2, DeepEval/Ragas y Protocolo MCP (vía `mcp` SDK oficial).

---

## 2. Arquitectura de Alto Nivel y Flujo de Datos

```
                                  [ Usuario / CLI ]
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │      SUBPROYECTO 5: AGENT HARNESS      │
                      │  - Runtime State Machine (LangGraph)   │
                      │  - Resiliencia, Timeouts, Guardrails   │
                      │  - Observabilidad (Trazas Langfuse)    │
                      └────┬──────────────┬──────────────┬─────┘
                           │              │              │
             ┌─────────────┘              │              └─────────────┐
             ▼                            ▼                            ▼
  ┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
  │ SUBPROYECTO 1: MCP  │      │ SUBPROYECTO 2: RAG  │      │ SUBPROYECTO 3: MEM  │
  │ Servidor de Tools:  │      │ Base de Directrices │      │ Memoria Semántica   │
  │ - Git Diff Reader   │      │ - Vector Store      │      │ - Perfil Usuario    │
  │ - AST File Inspector│      │ - Hybrid Retriever  │      │ - Reglas Aprobadas  │
  │ - Linter Runner     │      │ - Re-ranking        │      │ - Historial Sesión  │
  └─────────────────────┘      └─────────────────────┘      └─────────────────────┘
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │      SUBPROYECTO 4: EVALS SUITE        │
                      │  - Faithfulness / Context Recall       │
                      │  - Tool Call Accuracy (MCP Benchmarks) │
                      │  - Gate de CI/CD (DeepEval / Ragas)    │
                      └────────────────────────────────────────┘

```

---

## 3. Desglose de los 5 Subproyectos

### Subproyecto 1: Servidor MCP (`modules/mcp_server`)

* **Propósito:** Proveer un servidor de herramientas desacoplado que exponga utilidades locales del sistema de archivos y control de versiones sin acoplarse a un LLM específico.
* **Componentes clave:**
* Transporte: `stdio` (estándar para CLI/agentes locales).
* Primitivas expuestas:
* `tools/get_git_diff`: Obtiene cambios staged o de un rango de commits.
* `tools/read_source_file`: Inspecciona código fuente con limitación de rango de líneas.
* `tools/run_static_analysis`: Ejecuta linters locales (e.g., Flake8, Ruff o Semgrep) y retorna diagnósticos en JSON estructurado.




* **Dependencias:** `mcp>=1.0.0`, `gitpython`, `pydantic`.

### Subproyecto 2: Motor RAG (`modules/rag_engine`)

* **Propósito:** Indexar normativas de arquitectura, guías de estilo internas (OWASP Top 10, clean code guidelines, manuales de infraestructura) para sustentar las recomendaciones del auditor.
* **Componentes clave:**
* *Chunking:* Semantic / Markdown-aware chunking (tamaño de 512 tokens, 10% overlap).
* *Embeddings:* `text-embedding-3-small` (o alternativa local `all-MiniLM-L6-v2`).
* *Almacenamiento:* Qdrant o ChromaDB en modo embebido.
* *Pipeline de Recuperación:* Búsqueda semántica con umbral de corte por similitud coseno ($>0.72$) y formateador de contexto con citas explícitas de fuentes.


* **Dependencias:** `qdrant-client` o `chromadb`, `sentence-transformers`, `langchain-text-splitters`.

### Subproyecto 3: Sistema de Memoria Híbrida (`modules/memory_store`)

* **Propósito:** Evitar repetición de instrucciones, recordar preferencias del programador (ej. framework preferido, exclusiones de reglas) y mantener continuidad conversacional.
* **Componentes clave:**
* *Short-term (Episódica):* Checkpointer de grafo para retener el estado de la sesión activa (mensajes, llamadas a tools y respuestas).
* *Long-term (Semántica/Declarativa):* Extractor asíncrono de hechos. Si el usuario declara: *"No reportes advertencias sobre variables no usadas en tests"*, se extrae como tripla semántica y se guarda en una colección persistente para ser recuperada en futuras auditorías.


* **Dependencias:** `sqlite3` (para checkpoints locales) y almacén vectorial/clave-valor indexado para perfiles.

### Subproyecto 4: Suite de Evaluación (`modules/evals_suite`)

* **Propósito:** Garantizar que el agente no degrade su precisión, no invente directrices de seguridad y llame a las herramientas correctas con los argumentos válidos.
* **Componentes clave:**
* *Dataset de prueba:* Archivo `golden_dataset.json` con 30 casos de prueba (código vulnerable, preguntas de estándares, escenarios de conflicto).
* *Métricas:*
* **Faithfulness (Fidelidad):** Mide si el análisis se basa estrictamente en la documentación RAG recuperada.
* **Context Precision / Recall:** Evalúa la calidad del retrieval.
* **Tool Selection Accuracy:** Verifica si el agente invoca la herramienta MCP adecuada frente a una consulta.
* **JSON Schema Validity:** Verifica que las respuestas estructuradas pasen la validación Pydantic sin fallback de error.




* **Dependencias:** `deepeval` o `ragas`, `pytest`.

### Subproyecto 5: Orquestador y Harness (`modules/agent_harness`)

* **Propósito:** Runtime de ejecución del agente. Coordina los flujos de decisión, reintentos, validación de esquemas y observabilidad.
* **Componentes clave:**
* *Máquina de estados (StateGraph):* Nodos de entrada, análisis de intención, consulta de memoria/RAG, ejecución de herramientas MCP y síntesis final.
* *Guardrails y Resiliencia:* Límite estricto de pasos en bucles de razonamiento (máximo 6 iteraciones), validación de respuestas con Pydantic, manejo de excepciones con fallback determinista.
* *Observabilidad:* Integración de spans y traces (OpenTelemetry / Langfuse) para medir costo por token, latencia y árboles de ejecución.


* **Dependencias:** `langgraph`, `langchain-core`, `langfuse`, `pydantic`.

---
