"""Extractor de hechos semanticos y almacen clave-valor de perfiles (T9).

Extrae triplas semanticas desde declaraciones del usuario y persiste
perfiles de usuario (preferencias, reglas aprobadas, exclusiones) para
ser recuperadas en futuras auditorias.
"""

from __future__ import annotations

import ast
import os
import sqlite3
from datetime import datetime
from typing import Any

from agent_harness.contracts import PerfilUsuario


class TriplaSemantica:
    """Tripla (sujeto, predicado, objeto) extraida de declaraciones de usuario."""

    def __init__(self, sujeto: str, predicado: str, objeto: str) -> None:
        self.sujeto = sujeto
        self.predicado = predicado
        self.objeto = objeto
        self.timestamp = datetime.now(tz=None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sujeto": self.sujeto,
            "predicado": self.predicado,
            "objeto": self.objeto,
            "timestamp": self.timestamp.isoformat(),
        }


class PerfilStore:
    """Almacen clave-valor de perfiles de usuario sobre sqlite3."""

    def __init__(self, db_path: str = "./data/memory/perfiles.db") -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._crear_tablas()

    def _crear_tablas(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS perfiles (
                id_usuario TEXT PRIMARY KEY,
                framework_preferido TEXT,
                reglas_aprobadas TEXT,
                exclusiones TEXT,
                actualizado_en TEXT
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS triplas_semanticas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario TEXT,
                sujeto TEXT,
                predicado TEXT,
                objeto TEXT,
                timestamp TEXT
            )
            """
        )
        self._conn.commit()

    def guardar_perfil(self, perfil: PerfilUsuario) -> None:
        """Guarda o actualiza el perfil de un usuario."""
        self._conn.execute(
            """
            INSERT OR REPLACE INTO perfiles (id_usuario, framework_preferido, reglas_aprobadas, exclusiones, actualizado_en)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                perfil.id_usuario,
                perfil.framework_preferido,
                str(perfil.reglas_aprobadas),
                str(perfil.exclusiones),
                perfil.actualizado_en.isoformat(),
            ),
        )
        self._conn.commit()

    def cargar_perfil(self, id_usuario: str) -> PerfilUsuario | None:
        """Carga el perfil de un usuario si existe."""
        row = self._conn.execute(
            "SELECT * FROM perfiles WHERE id_usuario = ?", (id_usuario,)
        ).fetchone()
        if row is None:
            return None
        return PerfilUsuario(
            id_usuario=row["id_usuario"],
            framework_preferido=row["framework_preferido"],
            reglas_aprobadas=ast.literal_eval(row["reglas_aprobadas"]) if row["reglas_aprobadas"] else [],
            exclusiones=ast.literal_eval(row["exclusiones"]) if row["exclusiones"] else [],
            actualizado_en=datetime.fromisoformat(row["actualizado_en"]),
        )

    def guardar_tripla(self, id_usuario: str, tripla: TriplaSemantica) -> None:
        """Guarda una tripla semantica asociada a un usuario."""
        self._conn.execute(
            """
            INSERT INTO triplas_semanticas (id_usuario, sujeto, predicado, objeto, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (id_usuario, tripla.sujeto, tripla.predicado, tripla.objeto, tripla.timestamp.isoformat()),
        )
        self._conn.commit()

    def listar_triplas(self, id_usuario: str) -> list[dict[str, Any]]:
        """Lista todas las triplas semanticas de un usuario."""
        rows = self._conn.execute(
            "SELECT sujeto, predicado, objeto, timestamp FROM triplas_semanticas WHERE id_usuario = ?",
            (id_usuario,),
        ).fetchall()
        return [
            {"sujeto": r["sujeto"], "predicado": r["predicado"], "objeto": r["objeto"], "timestamp": r["timestamp"]}
            for r in rows
        ]

    def cerrar(self) -> None:
        self._conn.close()


class ExtractorHechos:
    """Extractor asincrono de hechos semanticos desde texto libre."""

    def extraer(self, texto: str) -> list[TriplaSemantica]:
        """Extrae triplas (sujeto, predicado, objeto) de una declaracion."""
        triplas: list[TriplaSemantica] = []

        texto_lower = texto.lower()

        # Patrones simples de extraccion de reglas y preferencias
        if "no reportar" in texto_lower or "no informes" in texto_lower:
            triplas.append(
                TriplaSemantica(sujeto="usuario", predicado="excluye_regla", objeto=texto)
            )
        if "framework" in texto_lower and ("prefiero" in texto_lower or "uso" in texto_lower):
            triplas.append(
                TriplaSemantica(sujeto="usuario", predicado="prefiere_framework", objeto=texto)
            )

        return triplas
