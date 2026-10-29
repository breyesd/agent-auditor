"""Servidor MCP base con transporte stdio para DSIA (Subproyecto 1).

Expone utilidades locales del sistema de archivos y control de versiones
sin acoplarse a un LLM específico. Punto de entrada para CLI/agentes locales.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from agent_harness.contracts import McpToolResult
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools.ast_file_inspector import ast_file_inspector
from .tools.get_git_diff import get_git_diff
from .tools.read_source_file import read_source_file
from .tools.run_static_analysis import run_static_analysis

_TOOLS: dict[str, Tool] = {}
_TOOL_HANDLERS: dict[str, callable] = {}


def register_tool(name: str, description: str, input_schema: dict[str, Any], handler: Callable) -> None:
    """Registra una herramienta MCP con su manejador."""
    _TOOLS[name] = Tool(
        name=name,
        description=description,
        inputSchema=input_schema,
    )
    _TOOL_HANDLERS[name] = handler


register_tool(
    name="get_git_diff",
    description="Obtiene cambios staged o de un rango de commits de un repositorio git",
    input_schema={
        "type": "object",
        "properties": {
            "ruta_repo": {"type": "string", "description": "Ruta al repositorio git"},
            "staged": {"type": "boolean", "description": "Si obtener cambios staged"},
            "commit_range": {"type": "string", "description": "Rango de commits (ej. HEAD~3..HEAD)"},
        },
    },
    handler=get_git_diff,
)

register_tool(
    name="read_source_file",
    description="Inspecciona código fuente con limitación de rango de líneas",
    input_schema={
        "type": "object",
        "required": ["ruta_archivo"],
        "properties": {
            "ruta_archivo": {"type": "string", "description": "Ruta al archivo fuente"},
            "linea_inicio": {"type": "integer", "description": "Línea inicial"},
            "linea_fin": {"type": "integer", "description": "Línea final"},
        },
    },
    handler=read_source_file,
)

register_tool(
    name="run_static_analysis",
    description="Ejecuta linters locales y retorna diagnósticos en JSON estructurado",
    input_schema={
        "type": "object",
        "properties": {
            "ruta_archivo": {"type": "string", "description": "Ruta al archivo o directorio"},
            "ruta_directorio": {"type": "string", "description": "Ruta al directorio"},
            "linter": {"type": "string", "description": "Linter a usar: ruff, flake8, semgrep"},
        },
    },
    handler=run_static_analysis,
)

register_tool(
    name="ast_file_inspector",
    description="Inspecciona un archivo Python usando AST y retorna metricas estructurales",
    input_schema={
        "type": "object",
        "required": ["ruta_archivo"],
        "properties": {
            "ruta_archivo": {"type": "string", "description": "Ruta al archivo Python a inspeccionar"},
        },
    },
    handler=ast_file_inspector,
)


async def _list_tools_handler(*args, **kwargs) -> list[Tool]:
    return list(_TOOLS.values())


async def _call_tool_handler(*args, **kwargs) -> list[TextContent]:
    # Los argumentos pueden venir en distintas posiciones según la versión del SDK
    arguments: dict[str, Any] = {}
    for kwarg_name in ("arguments", "args"):
        if kwarg_name in kwargs and kwargs[kwarg_name] is not None:
            arguments = kwargs[kwarg_name]
            break
    if not arguments and len(args) > 1:
        arguments = args[1] if isinstance(args[1], dict) else {}
    if not arguments:
        arguments = {}

    name: str = ""
    for kwarg_name in ("name",):
        if kwarg_name in kwargs:
            name = kwargs[kwarg_name]
            break
    if not name and len(args) > 0:
        name = args[0] if isinstance(args[0], str) else ""

    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        return [TextContent(type="text", content=f"Herramienta no encontrada: {name}")]

    try:
        result: McpToolResult = await handler(arguments) if asyncio.iscoroutinefunction(handler) else handler(arguments)
        payload = result.model_dump()
        return [TextContent(type="text", content=str(payload))]
    except Exception as exc:  # noqa: BLE001
        return [TextContent(type="text", content=f"Error ejecutando {name}: {exc}")]


app = Server(
    name="dsia-mcp-server",
    version="0.1.0",
    on_list_tools=_list_tools_handler,
    on_call_tool=_call_tool_handler,
)


async def run() -> None:
    """Arranca el servidor MCP sobre transporte stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="dsia-mcp-server",
                server_version="0.1.0",
                capabilities=app.get_capabilities(),
            ),
        )


def main() -> None:
    """Punto de entrada del servidor MCP."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
