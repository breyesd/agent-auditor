"""Herramienta MCP: run_static_analysis (T4).

Ejecuta linters locales (Ruff/Flake8/Semgrep) y retorna diagnósticos JSON.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


def _buscar_linter() -> str | None:
    for candidato in ("ruff", "flake8", "semgrep"):
        if shutil.which(candidato):
            return candidato
    return None


def run_static_analysis(arguments: dict[str, Any]) -> dict[str, Any]:
    """Ejecuta análisis estático sobre una ruta y retorna diagnósticos JSON."""
    ruta = arguments.get("ruta_archivo") or arguments.get("ruta_directorio", ".")
    linter = arguments.get("linter") or _buscar_linter()
    if not linter:
        return {"exito": False, "error": "No se encontró ningún linter (ruff/flake8/semgrep)", "datos": {}}

    try:
        if linter == "ruff":
            cmd = ["ruff", "check", "--output-format", "json", ruta]
        elif linter == "flake8":
            cmd = ["flake8", "--format", "json", ruta]
        else:  # semgrep
            cmd = ["semgrep", "--json", ruta]

        resultado = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=60)
        try:
            diagnosticos = json.loads(resultado.stdout) if resultado.stdout else []
        except json.JSONDecodeError:
            diagnosticos = [{"mensaje": resultado.stdout or resultado.stderr, "herramienta": linter}]

        return {
            "exito": resultado.returncode == 0,
            "datos": {
                "herramienta": linter,
                "diagnosticos": diagnosticos,
                "codigo_salida": resultado.returncode,
            },
        }
    except subprocess.TimeoutExpired:
        return {"exito": False, "error": "Tiempo de espera agotado en el linter", "datos": {}}
    except Exception as exc:  # noqa: BLE001
        return {"exito": False, "error": str(exc), "datos": {}}
