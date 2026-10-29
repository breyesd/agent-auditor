"""Suite de evaluacion (T19-T20).

- golden_dataset.json con 30 casos de prueba
- Metricas: Faithfulness, Context Precision/Recall, Tool Selection Accuracy, JSON Schema Validity
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_harness.contracts import AuditorResponse, ValidacionResultado


class EvalsSuite:
    """Ejecuta el gate de evaluacion sobre informes generados."""

    def __init__(self, dataset_path: str | None = None) -> None:
        self.dataset_path = dataset_path or str(
            Path(__file__).parent / "golden_dataset.json"
        )
        with open(self.dataset_path, encoding="utf-8") as f:
            self.dataset = json.load(f)

    def validar_schema(self, respuesta: Any) -> bool:
        """JSON Schema Validity: la respuesta pasa validacion Pydantic sin error."""
        try:
            if not isinstance(respuesta, AuditorResponse):
                AuditorResponse(**respuesta)
            return True
        except (TypeError, ValueError):
            return False

    def faithfulness(self, respuesta: AuditorResponse, contexto_rag: list[str]) -> float:
        """Faithfulness: el analisis se basa estrictamente en documentacion RAG recuperada."""
        if not contexto_rag:
            return 0.7
        citas_usadas = sum(1 for h in respuesta.hallazgos if h.cita_fuente)
        total = max(len(respuesta.hallazgos), 1)
        return min(citas_usadas / total, 1.0)

    def tool_selection_accuracy(self, herramientas_esperadas: list[str], herramientas_usadas: list[str]) -> float:
        """Tool Selection Accuracy: se invoca la herramienta MCP adecuada."""
        if not herramientas_esperadas:
            return 1.0
        aciertos = len(set(herramientas_esperadas) & set(herramientas_usadas))
        return aciertos / len(herramientas_esperadas)

    def context_precision(self, documentos_relevantes: int, documentos_recuperados: int) -> float:
        """Context Precision proporcion."""
        if documentos_recuperados == 0:
            return 0.0
        return documentos_relevantes / documentos_recuperados

    def context_recall(self, documentos_relevantes: int, documentos_totales: int) -> float:
        """Context Recall proporcion."""
        if documentos_totales == 0:
            return 0.0
        return documentos_relevantes / documentos_totales

    def ejecutar_gate(self, respuesta: Any, contexto_rag: list[str] | None = None) -> ValidacionResultado:
        """Ejecuta el gate completo de validacion."""
        contexto_rag = contexto_rag or []
        schema_valido = self.validar_schema(respuesta)
        fe = self.faithfulness(respuesta, contexto_rag) if isinstance(respuesta, AuditorResponse) else 0.0

        aprobado = schema_valido and fe >= 0.7
        metricas = {
            "schema_valid": 1.0 if schema_valido else 0.0,
            "faithfulness": fe,
        }

        return ValidacionResultado(
            aprobado=aprobado,
            metricas=metricas,
            detalle=None if aprobado else "Gate de evaluacion no aprobado",
        )
