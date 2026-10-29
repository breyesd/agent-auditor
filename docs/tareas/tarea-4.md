# T4: Implementar herramienta run_static_analysis

- **id**: T4
- **título**: Implementar herramienta run_static_analysis
- **descripción**: Exponer `tools/run_static_analysis` que ejecuta linters locales (Flake8/Ruff/Semgrep) y retorna diagnósticos en JSON estructurado.
- **tipo**: logica_negocio
- **tamaño**: mediana
- **dependencias**: [T1]
- **validaciones de campo**: salida JSON estructurado; maneja linter no instalado
- **librerias o métodos utilitarios**: `mcp`, subprocess, (ruff/flake8/semgrep)
- **interfaz de usuario**: CLI vía MCP
- **estructura de datos**: {diagnosticos: [{regla, mensaje, archivo, linea, severidad}]}
- **enlace a su HU**: docs/historias/hu-4.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 1)
- **estado**: [ ]
