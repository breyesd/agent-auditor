# T13: Implementar StateMachine LangGraph con nodos

- **id**: T13
- **título**: Implementar StateMachine LangGraph con nodos
- **descripción**: Máquina de estados (StateGraph) del `agent_harness` que coordina nodos de entrada, análisis de intención, consulta de memoria/RAG, ejecución de herramientas MCP y síntesis final. Máx. 6 iteraciones de razonamiento.
- **tipo**: logica_negocio
- **tamaño**: grande
- **dependencias**: [T10, T12]
- **validaciones de campo**: grafo ejecuta flujo completo; límite de 6 iteraciones respetado
- **librerias o métodos utilitarios**: `langgraph`, `langchain-core`
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: estado del grafo (mensajes, contexto, resultados de herramientas)
- **enlace a su HU**: docs/historias/hu-1.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 5)
- **estado**: [ ]
- **nota**: tarea grande (>6h); se sugiere partir en sub-tareas por nodo si excede 8h
