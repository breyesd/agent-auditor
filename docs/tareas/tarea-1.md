# T1: Crear servidor MCP base con transporte stdio

- **id**: T1
- **título**: Servidor MCP base con transporte stdio
- **descripción**: Configurar el esqueleto del servidor MCP (`modules/mcp_server`) con transporte stdio, inicialización del SDK `mcp` y esquema base de herramientas. Punto de entrada para CLI/agentes locales.
- **tipo**: configuracion
- **tamaño**: mediana
- **dependencias**: []
- **validaciones de campo**: servidor arranca y responde a `initialize` y `listTools`
- **librerias o métodos utilitarios**: `mcp>=1.0.0`, `pydantic`
- **interfaz de usuario**: CLI (stdio)
- **estructura de datos**: esquema de tool MCP (nombre, descripción, inputSchema)
- **enlace a su HU**: docs/historias/hu-4.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 1)
- **estado**: [ ]
