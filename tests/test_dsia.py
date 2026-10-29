"""Pruebas unitarias del agente auditor DSIA."""

from __future__ import annotations

import os
import sys

# Asegurar que src esté en el path ANTES de cualquier import local
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "modules"))


from agent_harness.contracts import (
    AuditorRequest,
    AuditorResponse,
    CheckpointSesion,
    Finding,
    Intencion,
    McpToolResult,
    PerfilUsuario,
    ResumenHallazgos,
    Severidad,
    TipoHallazgo,
)
from agent_harness.nodes import (
    NodoInput,
    NodoIntentAnalysis,
    NodoSynthesize,
    NodoValidate,
)
from evals_suite.suite import EvalsSuite
from mcp_server.tools.get_git_diff import get_git_diff
from mcp_server.tools.read_source_file import read_source_file
from mcp_server.tools.run_static_analysis import run_static_analysis
from memory_store.checkpoint_store import CheckpointStore
from memory_store.perfil_store import (
    ExtractorHechos,
    PerfilStore,
)
from rag_engine.chunking import ChunkingPipeline

# ---------------- Contratos Pydantic ----------------

def test_auditor_request_valido():
    req = AuditorRequest(ruta_archivo="/tmp/foo.py")
    assert req.ruta_archivo == "/tmp/foo.py"
    assert req.diff is None


def test_auditor_request_con_diff():
    req = AuditorRequest(diff="diff --git a/foo.py b/foo.py")
    assert req.diff == "diff --git a/foo.py b/foo.py"


def test_finding_creacion():
    f = Finding(
        tipo=TipoHallazgo.SEGURIDAD,
        severidad=Severidad.ALTA,
        archivo="src/foo.py",
        linea=42,
        descripcion="SQL injection",
        sugerencia="Usar consultas parametrizadas",
        cita_fuente="OWASP A03",
    )
    assert f.tipo == TipoHallazgo.SEGURIDAD
    assert f.severidad == Severidad.ALTA
    assert f.linea == 42
    assert f.cita_fuente == "OWASP A03"


def test_auditor_response_serializacion():
    resp = AuditorResponse(
        hallazgos=[
            Finding(
                tipo=TipoHallazgo.SEGURIDAD,
                severidad=Severidad.ALTA,
                archivo="x.py",
                descripcion="hallazgo",
                sugerencia="arreglar",
            )
        ],
        resumen=ResumenHallazgos(
            total=1,
            por_severidad={Severidad.ALTA: 1},
            por_tipo={TipoHallazgo.SEGURIDAD: 1},
        ),
    )
    data = resp.model_dump()
    assert data["resumen"]["total"] == 1


# ---------------- Nodos del harness ----------------

def test_nodo_input_normaliza_entrada():
    nodo = NodoInput()
    estado = nodo({"request": {"ruta_archivo": "test.py"}})
    assert isinstance(estado["request"], AuditorRequest)
    assert estado["request"].ruta_archivo == "test.py"
    assert estado["iteraciones"] == 0


def test_nodo_intent_analysis_clasifica():
    nodo = NodoIntentAnalysis()
    estado = {
        "request": AuditorRequest(diff="refactorizar esta funcion"),
        "iteraciones": 0,
    }
    resultado = nodo(estado)
    assert resultado["intencion"] == Intencion.REFACTOR
    assert resultado["iteraciones"] == 1


def test_nodo_intent_analysis_por_defecto_auditoria():
    nodo = NodoIntentAnalysis()
    estado = {"request": AuditorRequest(ruta_archivo="x.py"), "iteraciones": 0}
    resultado = nodo(estado)
    assert resultado["intencion"] == Intencion.AUDITORIA


def test_nodo_synthesize_genera_respuesta():
    nodo = NodoSynthesize()
    estado = {
        "request": AuditorRequest(ruta_archivo="test.py"),
        "contexto_rag": {"citas": ["OWASP A03"]},
        "resultados_mcp": {
            "static_analysis": {
                "exito": True,
                "datos": {
                    "diagnosticos": [
                        {"archivo": "test.py", "linea": 5, "mensaje": "variable no usada", "herramienta": "ruff"}
                    ]
                },
            }
        },
        "citas_rag": ["OWASP A03"],
        "reglas_activas": [],
        "exclusiones": [],
        "errores": [],
        "iteraciones": 1,
    }
    resultado = nodo(estado)
    assert isinstance(resultado["respuesta"], AuditorResponse)
    assert resultado["respuesta"].resumen.total >= 1


def test_nodo_validate_aprueba_sin_errores():
    nodo = NodoValidate()
    estado = {
        "respuesta": AuditorResponse(
            hallazgos=[],
            resumen=ResumenHallazgos(total=0),
            citas_rag=[],
        ),
        "errores": [],
    }
    resultado = nodo(estado)
    assert resultado["validacion"]["aprobado"] is True


def test_nodo_validate_rechaza_con_errores():
    nodo = NodoValidate()
    estado = {
        "respuesta": AuditorResponse(hallazgos=[], resumen=ResumenHallazgos(total=0)),
        "errores": ["error de MCP"],
    }
    resultado = nodo(estado)
    assert resultado["validacion"]["aprobado"] is False


# ---------------- Memoria ----------------

def test_checkpoint_store_guardar_y_cargar(tmp_path):
    db = tmp_path / "checkpoints.db"
    store = CheckpointStore(str(db))
    cp = CheckpointSesion(
        session_id="s1",
        mensajes=[{"rol": "usuario", "contenido": "hola"}],
        llamadas_tool=[],
        respuestas=[],
    )
    store.guardar(cp)
    cargado = store.cargar("s1")
    assert cargado is not None
    assert cargado.session_id == "s1"
    assert cargado.mensajes[0]["contenido"] == "hola"
    store.cerrar()


def test_checkpoint_store_cargar_inexistente(tmp_path):
    db = tmp_path / "checkpoints.db"
    store = CheckpointStore(str(db))
    assert store.cargar("noexiste") is None
    store.cerrar()


def test_perfil_store_guardar_y_cargar(tmp_path):
    db = tmp_path / "perfiles.db"
    store = PerfilStore(str(db))
    perfil = PerfilUsuario(
        id_usuario="u1",
        framework_preferido="django",
        reglas_aprobadas=["no-print"],
        exclusiones=["no-unused-in-tests"],
    )
    store.guardar_perfil(perfil)
    cargado = store.cargar_perfil("u1")
    assert cargado is not None
    assert cargado.framework_preferido == "django"
    assert "no-print" in cargado.reglas_aprobadas
    assert "no-unused-in-tests" in cargado.exclusiones
    store.cerrar()


def test_extractor_hechos_extrae_regla():
    extractor = ExtractorHechos()
    triplas = extractor.extraer("No reportar advertencias de variables no usadas")
    assert len(triplas) >= 1
    assert triplas[0].predicado == "excluye_regla"


# ---------------- RAG Chunking ----------------

def test_chunking_divide_en_chunks():
    pipeline = ChunkingPipeline(chunk_size=50, chunk_overlap=10)
    texto = "A " * 100  # ~200 chars
    chunks = pipeline.chunk_documento(texto, {"fuente": "test.md"})
    assert len(chunks) > 1
    for c in chunks:
        assert len(c["texto"]) <= 60
        assert c["metadata"]["fuente"] == "test.md"


# ---------------- Evals Suite ----------------

def test_evals_suite_valida_schema():
    suite = EvalsSuite()
    assert suite.validar_schema({"hallazgos": [], "resumen": {"total": 0}}) is True
    assert suite.validar_schema({"hallazgos": "no_es_lista"}) is False


def test_evals_suite_faithfulness():
    suite = EvalsSuite()
    resp = AuditorResponse(
        hallazgos=[
            Finding(
                tipo=TipoHallazgo.SEGURIDAD,
                severidad=Severidad.ALTA,
                archivo="x.py",
                descripcion="h",
                sugerencia="s",
                cita_fuente="OWASP",
            )
        ]
    )
    score = suite.faithfulness(resp, ["OWASP A03"])
    assert score == 1.0


def test_golden_dataset_tiene_30_casos():
    suite = EvalsSuite()
    assert len(suite.dataset["casos"]) == 30


# ---------------- Herramientas MCP ----------------

def test_read_source_file_archivo_inexistente():
    resultado = read_source_file({"ruta_archivo": "/no/existe.py"})
    assert resultado["exito"] is False
    assert "error" in resultado


def test_read_source_file_con_rango(tmp_path):
    archivo = tmp_path / "ejemplo.py"
    archivo.write_text("linea1\nlinea2\nlinea3\nlinea4\nlinea5\n")
    resultado = read_source_file({"ruta_archivo": str(archivo), "linea_inicio": 2, "linea_fin": 4})
    assert resultado["exito"] is True
    assert resultado["datos"]["linea_inicio"] == 2
    assert resultado["datos"]["linea_fin"] == 4
    assert "linea2" in resultado["datos"]["contenido"]
    assert "linea4" in resultado["datos"]["contenido"]


def test_run_static_analysis_sin_linter(monkeypatch):
    import mcp_server.tools.run_static_analysis as mod

    monkeypatch.setattr(mod.shutil, "which", lambda x: None)
    resultado = run_static_analysis({"ruta_archivo": "test.py"})
    assert resultado["exito"] is False
    assert "No se encontr" in resultado["error"]


def test_get_git_diff_no_es_repositorio(tmp_path):
    resultado = get_git_diff({"ruta_repo": str(tmp_path), "staged": True})
    assert resultado["exito"] is False
    assert "No es un repositorio git" in resultado["error"]


# ---------------- Validaciones de campo (Pydantic) ----------------

def test_mcp_tool_result_valido():
    r = McpToolResult(herramienta="get_git_diff", exito=True, datos={"diff": "..."})
    assert r.herramienta == "get_git_diff"
    assert r.exito is True


def test_perfil_usuario_valores_default():
    p = PerfilUsuario()
    assert p.id_usuario is not None
    assert p.framework_preferido is None
    assert p.reglas_aprobadas == []
