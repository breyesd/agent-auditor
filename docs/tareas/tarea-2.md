# T2: Implementar herramienta get_git_diff

- **id**: T2
- **título**: Implementar herramienta get_git_diff
- **descripción**: Exponer `tools/get_git_diff` que obtiene cambios staged o de un rango de commits usando GitPython.
- **tipo**: logica_negocio
- **tamaño**: mediana
- **dependencias**: [T1]
- **validaciones de campo**: retorna diff válido para staged y rango de commits; maneja repositorio sin cambios
- **librerias o métodos utilitarios**: `gitpython`, `mcp`
- **interfaz de usuario**: CLI vía MCP
- **estructura de datos**: {diff: string, commits: string[], staged: bool}
- **enlace a su HU**: docs/historias/hu-4.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 1)
- **estado**: [ ]
