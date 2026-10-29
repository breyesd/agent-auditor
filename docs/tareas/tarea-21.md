# T21: Integrar observabilidad OpenTelemetry/Langfuse

- **id**: T21
- **título**: Integrar observabilidad OpenTelemetry/Langfuse
- **descripción**: Integración de spans y traces (OpenTelemetry / Langfuse) para medir costo por token, latencia y árboles de ejecución por nodo del grafo.
- **tipo**: configuracion
- **tamaño**: mediana
- **dependencias**: [T13]
- **validaciones de campo**: spans emitidos por nodo; trazas visibles en Langfuse/OpenTelemetry
- **librerias o métodos utilitarios**: `langfuse`, `opentelemetry`
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: traces {span_id, nodo, latencia, tokens, costo}
- **enlace a su HU**: docs/historias/hu-1.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 5)
- **estado**: [ ]
