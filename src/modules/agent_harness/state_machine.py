"""StateMachine LangGraph (T13).

Maquina de estados del agent_harness que coordina los nodos de entrada,
analisis de intención, consulta de memoria/RAG, ejecucion de herramientas
MCP y sintesis final. Maximo 6 iteraciones de razonamiento.
"""

from __future__ import annotations

from typing import Any

from agent_harness.contracts import AuditorRequest
from agent_harness.nodes import (
    NodoInput,
    NodoIntentAnalysis,
    NodoMcpExecute,
    NodoMemoryConsult,
    NodoRagRetrieve,
    NodoSynthesize,
    NodoValidate,
)
from langgraph.graph import END, StateGraph

MAX_ITERACIONES = 6


class HarnessState(dict[str, Any]):
    """Estado del grafo del harness."""


class AuditorHarness:
    """Orquestador basado en LangGraph StateMachine."""

    def __init__(self) -> None:
        self._grafo = self._construir_grafo()

    def _construir_grafo(self) -> StateGraph:
        workflow = StateGraph(HarnessState)

        workflow.add_node("input", NodoInput())
        workflow.add_node("intent_analysis", NodoIntentAnalysis())
        workflow.add_node("memory_consult", NodoMemoryConsult())
        workflow.add_node("rag_retrieve", NodoRagRetrieve())
        workflow.add_node("mcp_execute", NodoMcpExecute())
        workflow.add_node("synthesize", NodoSynthesize())
        workflow.add_node("validate", NodoValidate())

        workflow.set_entry_point("input")
        workflow.add_edge("input", "intent_analysis")
        workflow.add_edge("intent_analysis", "memory_consult")
        workflow.add_edge("memory_consult", "rag_retrieve")
        workflow.add_edge("rag_retrieve", "mcp_execute")
        workflow.add_edge("mcp_execute", "synthesize")
        workflow.add_edge("synthesize", "validate")
        workflow.add_edge("validate", END)

        return workflow.compile()

    def auditar(
        self,
        request: AuditorRequest,
        id_usuario: str = "default",
        max_iteraciones: int = MAX_ITERACIONES,
    ) -> dict[str, Any]:
        """Ejecuta el flujo completo de auditoria."""
        estado_inicial: HarnessState = {
            "request": request.model_dump(),
            "id_usuario": id_usuario,
            "iteraciones": 0,
            "max_iteraciones": max_iteraciones,
        }

        resultado = self._grafo.invoke(estado_inicial)
        return resultado
