"""Herramienta MCP: read_source_file (T3).

Inspecciona código fuente con limitación de rango de líneas.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def read_source_file(arguments: dict[str, Any]) -> dict[str, Any]:
    """Lee un archivo fuente con rango de líneas opcional."""
    ruta = arguments.get("ruta_archivo")
    if not ruta:
        return {"exito": False, "error": "ruta_archivo es requerido", "datos": {}}

    path = Path(ruta)
    if not path.exists():
        return {"exito": False, "error": f"Archivo no encontrado: {ruta}", "datos": {}}

    try:
        lineas = path.read_text(encoding="utf-8").splitlines()
        total = len(lineas)
        inicio = arguments.get("linea_inicio", 1)
        fin = arguments.get("linea_fin", total)
        inicio = max(1, min(inicio, total))
        fin = max(inicio, min(fin, total))
        contenido = "\n".join(lineas[inicio - 1 : fin])
        return {
            "exito": True,
            "datos": {
                "contenido": contenido,
                "linea_inicio": inicio,
                "linea_fin": fin,
                "total_lineas": total,
                "archivo": str(path),
            },
        }
    except Exception as exc:  # noqa: BLE001
        return {"exito": False, "error": str(exc), "datos": {}}
