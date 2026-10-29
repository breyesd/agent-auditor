"""CLI de entrada y validacion Pydantic (T12).

Acepta ruta de archivo o diff staged, normaliza la entrada y valida
el esquema AuditorRequest antes de pasar al harness.
"""

from __future__ import annotations

import typer
from agent_harness.contracts import AuditorRequest, AuditorResponse
from agent_harness.nodes import (
    NodoInput,
    NodoIntentAnalysis,
    NodoMcpExecute,
    NodoMemoryConsult,
    NodoRagRetrieve,
    NodoSynthesize,
    NodoValidate,
)
from rich import print as rprint

app = typer.Typer(name="dsia", help="DevSecOps Intelligent Auditor")


def _construir_estado(request: AuditorRequest, id_usuario: str = "default") -> dict:
    estado: dict = {"request": request.model_dump(), "id_usuario": id_usuario}
    for nodo in (
        NodoInput(),
        NodoIntentAnalysis(),
        NodoMemoryConsult(),
        NodoRagRetrieve(),
        NodoMcpExecute(),
        NodoSynthesize(),
        NodoValidate(),
    ):
        estado = nodo(estado)
    return estado


@app.command()
def auditar(
    ruta_archivo: str | None = typer.Argument(None, help="Ruta al archivo a auditar"),
    diff: str | None = typer.Option(None, "--diff", help="Diff o cambios staged"),
    reglas: str | None = typer.Option(None, "--reglas", help="Reglas personalizadas separadas por comas"),
    exclusiones: str | None = typer.Option(None, "--exclusiones", help="Exclusiones separadas por comas"),
    id_usuario: str = typer.Option("default", "--usuario", help="Identificador de usuario"),
    json_out: bool = typer.Option(False, "--json", help="Salida en formato JSON"),
) -> None:
    """Ejecuta una auditoria de codigo sobre un archivo o diff."""
    reglas_lista = [r.strip() for r in reglas.split(",")] if reglas else None
    exclusiones_lista = [e.strip() for e in exclusiones.split(",")] if exclusiones else None

    request = AuditorRequest(
        ruta_archivo=ruta_archivo,
        diff=diff,
        reglas_personalizadas=reglas_lista,
        exclusiones=exclusiones_lista,
    )

    estado = _construir_estado(request, id_usuario)
    respuesta: AuditorResponse = estado["respuesta"]

    if json_out:
        rprint(respuesta.model_dump_json(indent=2))
    else:
        rprint("[bold]Resumen de auditoria[/bold]")
        rprint(f"Total hallazgos: {respuesta.resumen.total}")
        for sev, count in respuesta.resumen.por_severidad.items():
            if count:
                rprint(f"  {sev.value}: {count}")
        for h in respuesta.hallazgos:
            rprint(f"  - [{h.severidad.value}] {h.tipo.value}: {h.descripcion} ({h.archivo}:{h.linea})")


@app.command()
def servidor_mcp() -> None:
    """Arranca el servidor MCP sobre stdio."""
    from mcp_server.server import main

    main()


if __name__ == "__main__":
    app()
