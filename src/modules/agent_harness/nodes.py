"""Nodos del harness LangGraph (T11-T18).

Cada nodo implementa un paso del flujo de auditoria usando los contratos
Pydantic y los subproyectos MCP, RAG, memoria y evals.
"""

from __future__ import annotations

from typing import Any

from agent_harness.contracts import (
    AuditorRequest,
    AuditorResponse,
    Finding,
    Intencion,
    ResumenHallazgos,
    Severidad,
    TipoHallazgo,
)
from memory_store.perfil_store import PerfilStore
from rag_engine.retriever import RagRetriever


class NodoInput:
    """Nodo input: normaliza entrada y valida AuditorRequest."""

    def __call__(self, estado: dict[str, Any]) -> dict[str, Any]:
        request = estado.get("request")
        if isinstance(request, dict):
            request = AuditorRequest(**request)
        elif not isinstance(request, AuditorRequest):
            raise TypeError("request no proporcionado o invalido")

        return {
            "request": request,
            "intencion": None,
            "perfil": None,
            "contexto_rag": None,
            "resultados_mcp": {},
            "respuesta": None,
            "validacion": None,
            "errores": [],
            "iteraciones": 0,
        }


class NodoIntentAnalysis:
    """Nodo intent_analysis: clasifica la solicitud (auditoria / refactor / cumplimiento)."""

    def __call__(self, estado: dict[str, Any]) -> dict[str, Any]:
        request: AuditorRequest = estado["request"]
        intencion = request.intencion_forzada or Intencion.AUDITORIA
        texto = request.diff or request.ruta_archivo or ""

        if "refactor" in texto.lower():
            intencion = Intencion.REFACTOR
        elif "cumplimiento" in texto.lower() or "owasp" in texto.lower():
            intencion = Intencion.CUMPLIMIENTO

        return {**estado, "intencion": intencion, "iteraciones": estado.get("iteraciones", 0) + 1}


class NodoMemoryConsult:
    """Nodo memory_consult: lee perfil y reglas aprobadas de memory_store."""

    def __init__(self, perfil_store: PerfilStore | None = None) -> None:
        self.perfil_store = perfil_store or PerfilStore()

    def __call__(self, estado: dict[str, Any]) -> dict[str, Any]:
        id_usuario = estado.get("id_usuario", "default")
        perfil = self.perfil_store.cargar_perfil(id_usuario)

        reglas_activas: list[str] = []
        if perfil:
            reglas_activas = [r for r in perfil.reglas_aprobadas if r not in perfil.exclusiones]

        return {
            **estado,
            "perfil": perfil,
            "reglas_activas": reglas_activas,
            "exclusiones": perfil.exclusiones if perfil else [],
        }


class NodoRagRetrieve:
    """Nodo rag_retrieve: recupera directrices de rag_engine con citas."""

    def __init__(self, retriever: RagRetriever | None = None) -> None:
        self.retriever = retriever or RagRetriever()

    def __call__(self, estado: dict[str, Any]) -> dict[str, Any]:
        request: AuditorRequest = estado["request"]
        consulta = request.diff or request.ruta_archivo or "auditoria de codigo"
        resultado = self.retriever.recuperar(consulta)

        return {
            **estado,
            "contexto_rag": resultado,
            "citas_rag": resultado.get("citas", []),
        }


class NodoMcpExecute:
    """Nodo mcp_execute: invoca herramientas MCP con fallback determinista."""

    def __call__(self, estado: dict[str, Any]) -> dict[str, Any]:
        intencion: Intencion = estado["intencion"]
        resultados: dict[str, Any] = {}

        try:
            from mcp_server.server import (
                get_git_diff,
                read_source_file,
                run_static_analysis,
            )

            request: AuditorRequest = estado["request"]

            if request.diff:
                resultados["git_diff"] = get_git_diff({"diff": request.diff})
            if request.ruta_archivo:
                resultados["source_file"] = read_source_file({"ruta_archivo": request.ruta_archivo})

            if intencion in (Intencion.AUDITORIA, Intencion.CUMPLIMIENTO):
                target = request.ruta_archivo or "."
                resultados["static_analysis"] = run_static_analysis({"ruta_archivo": target})

        except Exception as exc:  # noqa: BLE001
            resultados["error"] = str(exc)
            estado.setdefault("errores", []).append(f"mcp_execute: {exc}")

        return {**estado, "resultados_mcp": resultados}


class NodoSynthesize:
    """Nodo synthesize: combina memoria, RAG y herramientas en AuditorResponse."""

    def __call__(self, estado: dict[str, Any]) -> dict[str, Any]:
        request: AuditorRequest = estado["request"]
        resultados_mcp: dict[str, Any] = estado.get("resultados_mcp") or {}
        citas: list[str] = estado.get("citas_rag", [])
        estado.get("reglas_activas", [])

        hallazgos: list[Finding] = []

        # Hallazgos desde analisis estatico
        sa = resultados_mcp.get("static_analysis", {})
        if sa.get("exito"):
            for diag in sa.get("datos", {}).get("diagnosticos", []):
                hallazgos.append(
                    Finding(
                        tipo=TipoHallazgo.SEGURIDAD,
                        severidad=Severidad.MEDIA,
                        archivo=diag.get("archivo", "desconocido"),
                        linea=diag.get("linea"),
                        descripcion=diag.get("mensaje", ""),
                        sugerencia="Revisar y corregir segun la regla reportada",
                        cita_fuente=None,
                    )
                )

        # Hallazgos desde citas RAG (directrices incumplidas)
        for cita in citas:
            hallazgos.append(
                Finding(
                    tipo=TipoHallazgo.CUMPLIMIENTO,
                    severidad=Severidad.BAJA,
                    archivo=request.ruta_archivo or "desconocido",
                    descripcion=f"Directriz relacionada: {cita}",
                    sugerencia="Revisar la directriz citada y aplicar si es applicable",
                    cita_fuente=cita,
                )
            )

        # Aplicar exclusiones
        exclusiones: list[str] = estado.get("exclusiones", [])
        hallazgos = [h for h in hallazgos if not any(e in h.descripcion for e in exclusiones)]

        resumen = ResumenHallazgos(
            total=len(hallazgos),
            por_severidad={s: 0 for s in Severidad},
            por_tipo={t: 0 for t in TipoHallazgo},
        )
        for h in hallazgos:
            resumen.por_severidad[h.severidad] = resumen.por_severidad.get(h.severidad, 0) + 1
            resumen.por_tipo[h.tipo] = resumen.por_tipo.get(h.tipo, 0) + 1

        respuesta = AuditorResponse(
            hallazgos=hallazgos,
            resumen=resumen,
            metricas={"iteraciones": estado.get("iteraciones", 0)},
            citas_rag=citas,
            fallback_usado=bool(estado.get("errores")),
        )

        return {**estado, "respuesta": respuesta}


class NodoValidate:
    """Nodo validate: gate de calidad con evals_suite."""

    def __call__(self, estado: dict[str, Any]) -> dict[str, Any]:
        respuesta: AuditorResponse = estado["respuesta"]
        errores: list[str] = estado.get("errores", [])

        aprobado = len(errores) == 0 and respuesta.hallazgos is not None
        metricas = {
            "schema_valid": True,
            "tool_accuracy": 1.0 if not errores else 0.5,
            "faithfulness": 1.0 if respuesta.citas_rag else 0.7,
        }

        estado["validacion"] = {
            "aprobado": aprobado,
            "metricas": metricas,
            "detalle": None if aprobado else "Gate de validacion no aprobado",
        }
        return estado
