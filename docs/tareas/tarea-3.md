# T3: Implementar herramienta read_source_file

- **id**: T3
- **título**: Implementar herramienta read_source_file
- **descripción**: Exponer `tools/read_source_file` para inspeccionar código fuente con limitación de rango de líneas.
- **tipo**: logica_negocio
- **tamaño**: pequena
- **dependencias**: [T1]
- **validaciones de campo**: respeta rango de líneas solicitado; maneja archivo inexistente
- **librerias o métodos utilitarios**: `mcp`, pathlib
- **interfaz de usuario**: CLI vía MCP
- **estructura de datos**: {contenido: string, linea_inicio: int, linea_fin: int, total_lineas: int}
- **enlace a su HU**: docs/historias/hu-4.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 1)
- **estado**: [ ]
