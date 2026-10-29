"""Contratos Pydantic compartidos entre los 5 subproyectos de DSIA.

Todos los componentes se comunican mediante esquemas JSON estrictos validados con Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Severidad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class TipoHallazgo(str, Enum):
    SEGURIDAD = "seguridad"
    CUMPLIMIENTO = "cumplimiento"
    ESTILO = "estilo"
    REFACTOR = "refactor"


class Intencion(str, Enum):
    AUDITORIA = "auditoria"
    REFACTOR = "refactor"
    CUMPLIMIENTO = "cumplimiento"


class Finding(BaseModel):
    """Un hallazgo de auditoría individual."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    tipo: TipoHallazgo
    severidad: Severidad
    archivo: str
    linea: int | None = None
    descripcion: str
    sugerencia: str
    cita_fuente: str | None = None


class ResumenHallazgos(BaseModel):
    total: int = 0
    por_severidad: dict[Severidad, int] = Field(default_factory=dict)
    por_tipo: dict[TipoHallazgo, int] = Field(default_factory=dict)


class AuditorRequest(BaseModel):
    """Solicitud de auditoría de entrada."""

    ruta_archivo: str | None = None
    diff: str | None = None
    reglas_personalizadas: list[str] | None = None
    exclusiones: list[str] | None = None
    intencion_forzada: Intencion | None = None


class RagContext(BaseModel):
    """Contexto recuperado del motor RAG con citas."""

    documentos: list[str] = Field(default_factory=list)
    puntuaciones: list[float] = Field(default_factory=list)
    citas: list[str] = Field(default_factory=list)
    umbral_alcanzado: bool = False


class McpToolResult(BaseModel):
    """Resultado de una herramienta MCP."""

    herramienta: str
    exito: bool
    datos: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class PerfilUsuario(BaseModel):
    """Perfil de usuario con preferencias y reglas aprobadas."""

    id_usuario: str = Field(default_factory=lambda: str(uuid4()))
    framework_preferido: str | None = None
    reglas_aprobadas: list[str] = Field(default_factory=list)
    exclusiones: list[str] = Field(default_factory=list)
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)


class CheckpointSesion(BaseModel):
    """Checkpoint de memoria episódica para una sesión activa."""

    session_id: str
    mensajes: list[dict[str, Any]] = Field(default_factory=list)
    llamadas_tool: list[dict[str, Any]] = Field(default_factory=list)
    respuestas: list[dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditorResponse(BaseModel):
    """Respuesta completa de auditoría."""

    hallazgos: list[Finding] = Field(default_factory=list)
    resumen: ResumenHallazgos = Field(default_factory=ResumenHallazgos)
    metricas: dict[str, Any] = Field(default_factory=dict)
    citas_rag: list[str] = Field(default_factory=list)
    fallback_usado: bool = False


class ValidacionResultado(BaseModel):
    """Resultado del gate de validación (evals_suite)."""

    aprobado: bool
    metricas: dict[str, float] = Field(default_factory=dict)
    detalle: str | None = None
