# HU-4: Ejecutar herramientas MCP (diff, lectura de archivo, linter)

Como usuario, quiero que el agente acceda a utilidades locales del sistema de archivos y control de versiones a través de un servidor MCP desacoplado.

## Especificación funcional de flujo de datos
1. `mcp_server` expone herramientas vía transporte stdio.
2. `tools/get_git_diff`: obtiene cambios staged o rango de commits.
3. `tools/read_source_file`: inspecciona código fuente con rango de líneas.
4. `tools/run_static_analysis`: ejecuta linters (Flake8/Ruff/Semgrep) y retorna diagnósticos JSON.
5. `agent_harness` invoca herramientas según intención detectada.

## Criterios de aceptación
- [ ] Transporte stdio operativo.
- [ ] get_git_diff retorna diff staged o rango de commits.
- [ ] read_source_file soporta limitación de rango de líneas.
- [ ] run_static_analysis retorna diagnósticos en JSON estructurado.
- [ ] Dependencias: mcp>=1.0.0, gitpython, pydantic.

## Relación
Especificación específica: docs/especificaciones/especificacion-fase-1.md (sección 2.2 nodo mcp_execute).
Subproyecto 1: modules/mcp_server.
