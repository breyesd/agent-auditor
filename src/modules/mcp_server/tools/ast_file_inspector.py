"""Herramienta MCP: ast_file_inspector.

Inspecciona código fuente Python usando el árbol de sintaxis abstracta (AST)
de la librería estándar y retorna métricas estructurales del archivo.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def _contar_complejidad(nodo: ast.AST) -> int:
    """Cuenta constructos que aumentan la complejidad ciclomatica."""
    complejidad = 1  # linea base
    for hijo in ast.walk(nodo):
        if isinstance(
            hijo,
            (
                ast.If,
                ast.For,
                ast.While,
                ast.Try,
                ast.ExceptHandler,
                ast.With,
                ast.BoolOp,
            ),
        ):
            complejidad += 1
    return complejidad


def ast_file_inspector(arguments: dict[str, Any]) -> dict[str, Any]:
    """Inspecciona un archivo Python y retorna metricas del AST."""
    ruta = arguments.get("ruta_archivo")
    if not ruta:
        return {"exito": False, "error": "ruta_archivo es requerido", "datos": {}}

    path = Path(ruta)
    if not path.exists():
        return {"exito": False, "error": f"Archivo no encontrado: {ruta}", "datos": {}}

    try:
        fuente = path.read_text(encoding="utf-8")
        arbol = ast.parse(fuente, filename=str(path))

        funciones = 0
        clases = 0
        imports = 0
        docstring_modulo = ast.get_docstring(arbol)

        for nodo in ast.walk(arbol):
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funciones += 1
            elif isinstance(nodo, (ast.ClassDef,)):
                clases += 1
            elif isinstance(nodo, (ast.Import, ast.ImportFrom)):
                imports += 1

        complejidad = _contar_complejidad(arbol)

        return {
            "exito": True,
            "datos": {
                "archivo": str(path),
                "funciones": funciones,
                "clases": clases,
                "imports": imports,
                "complejidad_ciclomatica": complejidad,
                "docstring_modulo": docstring_modulo,
                "nodos_totales": len(list(ast.walk(arbol))),
            },
        }
    except SyntaxError as exc:
        return {
            "exito": False,
            "error": f"Error de sintaxis en {ruta}: {exc}",
            "datos": {},
        }
    except Exception as exc:  # noqa: BLE001
        return {"exito": False, "error": str(exc), "datos": {}}
