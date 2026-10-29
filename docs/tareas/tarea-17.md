# T17: Implementar nodo mcp_execute

- **id**: T17
- **título**: Implementar nodo mcp_execute
- **descripción**: Nodo que invoca herramientas de `mcp_server` (get_git_diff, read_source_file, run_static_analysis) según la intención detectada, con fallback determinista ante fallo.
- **tipo**: logica_negocio
- **tamaño**: pequena
- **dependencias**: [T1, T2, T3, T4]
- **validaciones de campo**: ejecuta herramienta adecuada; fallback ante error sin bloquear
- **librerias o métodos utilitarios**: `mcp`, cliente MCP stdio
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: `McpToolResult`
- **enlace a su HU**: docs/historias/hu-4.md, docs/historias/hu-1.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 1, 5)
- **estado**: [ ]
