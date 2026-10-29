"""Observabilidad OpenTelemetry / Langfuse (T21).

Integracion de spans y traces para medir costo por token, latencia y
arboles de ejecucion por nodo del grafo.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


class Observabilidad:
    """Configuracion y utilidades de trazabilidad para el harness."""

    def __init__(self, nombre_servicio: str = "dsia-agent-harness") -> None:
        self.nombre_servicio = nombre_servicio
        self.habilitado = os.getenv("DSIA_OBSERVABILIDAD", "true").lower() == "true"
        self._trazador = None
        if self.habilitado:
            self._configurar_trazador()

    def _configurar_trazador(self) -> None:
        proveedor = TracerProvider()
        proveedor.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(proveedor)
        self._trazador = trace.get_tracer(self.nombre_servicio)

    @contextmanager
    def span(self, nombre: str, atributos: dict[str, Any] | None = None):
        """Crea un span OpenTelemetry para un nodo del grafo."""
        if self._trazador is None:
            yield None
            return
        with self._trazador.start_as_current_span(nombre) as span:
            if atributos:
                for clave, valor in atributos.items():
                    span.set_attribute(clave, str(valor))
            inicio = time.time()
            try:
                yield span
            finally:
                duracion = time.time() - inicio
                span.set_attribute("duracion_segundos", duracion)


observabilidad = Observabilidad()
