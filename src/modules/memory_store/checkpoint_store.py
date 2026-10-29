"""Almacén sqlite3 para checkpoints de memoria episódica (Subproyecto 3).

Retiene el estado de sesión activa: mensajes, llamadas a tools y respuestas.
"""

from __future__ import annotations

import ast
import os
import sqlite3
from datetime import datetime

from agent_harness.contracts import CheckpointSesion


class CheckpointStore:
    """Almacén persistente de checkpoints de sesión sobre sqlite3."""

    def __init__(self, db_path: str = "./data/memory/checkpoints.db") -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._crear_tabla()

    def _crear_tabla(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS checkpoints (
                session_id TEXT PRIMARY KEY,
                mensajes TEXT,
                llamadas_tool TEXT,
                respuestas TEXT,
                timestamp TEXT
            )
            """
        )
        self._conn.commit()

    def guardar(self, checkpoint: CheckpointSesion) -> None:
        """Guarda o actualiza el checkpoint de una sesión."""
        self._conn.execute(
            """
            INSERT OR REPLACE INTO checkpoints (session_id, mensajes, llamadas_tool, respuestas, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                checkpoint.session_id,
                str(checkpoint.mensajes),
                str(checkpoint.llamadas_tool),
                str(checkpoint.respuestas),
                checkpoint.timestamp.isoformat(),
            ),
        )
        self._conn.commit()

    def cargar(self, session_id: str) -> CheckpointSesion | None:
        """Carga el checkpoint de una sesión si existe."""
        row = self._conn.execute(
            "SELECT * FROM checkpoints WHERE session_id = ?", (session_id,)
        ).fetchone()
        if row is None:
            return None
        return CheckpointSesion(
            session_id=row["session_id"],
            mensajes=ast.literal_eval(row["mensajes"]) if row["mensajes"] else [],
            llamadas_tool=ast.literal_eval(row["llamadas_tool"]) if row["llamadas_tool"] else [],
            respuestas=ast.literal_eval(row["respuestas"]) if row["respuestas"] else [],
            timestamp=datetime.fromisoformat(row["timestamp"]),
        )

    def cerrar(self) -> None:
        self._conn.close()
