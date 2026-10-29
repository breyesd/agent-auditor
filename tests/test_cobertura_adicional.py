"""Pruebas adicionales de cobertura para DSIA."""

from __future__ import annotations

import os
import sys

import pytest
from typer.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "modules"))

from agent_harness.cli import app
from agent_harness.contracts import (
    AuditorRequest,
    AuditorResponse,
    Intencion,
    ResumenHallazgos,
    ValidacionResultado,
)
from agent_harness.nodes import (
    NodoMcpExecute,
    NodoMemoryConsult,
    NodoRagRetrieve,
    NodoSynthesize,
    NodoValidate,
)
from agent_harness.observabilidad import Observabilidad
from agent_harness.state_machine import MAX_ITERACIONES, AuditorHarness
from evals_suite.suite import EvalsSuite
from mcp_server.server import _TOOLS, register_tool
from mcp_server.tools.ast_file_inspector import ast_file_inspector
from mcp_server.tools.get_git_diff import get_git_diff
from mcp_server.tools.run_static_analysis import run_static_analysis
from memory_store.perfil_store import ExtractorHechos, PerfilStore, TriplaSemantica
from rag_engine.chunking import ChunkingPipeline
from rag_engine.retriever import EmbeddingModel, RagRetriever
from rag_engine.vector_store import VectorStore, VectorStoreConfig

runner = CliRunner()


# ---------------- CLI ----------------

def test_cli_auditar_comando_existe():
    result = runner.invoke(app, ["auditar", "--help"])
    assert result.exit_code == 0


def test_cli_servidor_mcp_comando_existe():
    result = runner.invoke(app, ["servidor-mcp", "--help"])
    assert result.exit_code == 0


# ---------------- Nodos ----------------

def test_nodo_memory_consult_con_perfil():
    nodo = NodoMemoryConsult()
    estado = {
        "request": AuditorRequest(ruta_archivo="test.py"),
        "id_usuario": "u1",
        "perfil": None,
        "reglas_activas": [],
        "exclusiones": [],
    }
    resultado = nodo(estado)
    assert "perfil" in resultado
    assert "reglas_activas" in resultado
    assert "exclusiones" in resultado


def test_nodo_rag_retrieve_sin_contexto():
    nodo = NodoRagRetrieve()
    estado = {
        "request": AuditorRequest(ruta_archivo="test.py"),
        "contexto_rag": None,
        "citas_rag": [],
    }
    resultado = nodo(estado)
    assert "contexto_rag" in resultado
    assert "citas_rag" in resultado


def test_nodo_mcp_execute_con_errores():
    nodo = NodoMcpExecute()
    estado = {
        "request": AuditorRequest(diff="diff prueba"),
        "intencion": Intencion.AUDITORIA,
        "errores": [],
        "resultados_mcp": {},
    }
    resultado = nodo(estado)
    assert "resultados_mcp" in resultado


def test_nodo_synthesize_con_exclusiones():
    nodo = NodoSynthesize()
    estado = {
        "request": AuditorRequest(ruta_archivo="test.py"),
        "contexto_rag": {"citas": []},
        "resultados_mcp": {},
        "citas_rag": [],
        "reglas_activas": [],
        "exclusiones": ["variable no usada"],
        "errores": [],
        "iteraciones": 0,
    }
    resultado = nodo(estado)
    assert isinstance(resultado["respuesta"], AuditorResponse)


def test_nodo_validate_detalle():
    nodo = NodoValidate()
    estado = {
        "respuesta": AuditorResponse(hallazgos=[], resumen=ResumenHallazgos(total=0)),
        "errores": ["fallo"],
    }
    resultado = nodo(estado)
    assert resultado["validacion"]["aprobado"] is False
    assert "detalle" in resultado["validacion"]


# ---------------- Observabilidad ----------------

def test_observabilidad_desactivada(monkeypatch):
    monkeypatch.setenv("DSIA_OBSERVABILIDAD", "false")
    obs = Observabilidad()
    assert obs.habilitado is False
    with obs.span("test_span", {"clave": "valor"}) as span:
        assert span is None


def test_observabilidad_activada(monkeypatch):
    monkeypatch.setenv("DSIA_OBSERVABILIDAD", "true")
    obs = Observabilidad()
    assert obs.habilitado is True
    assert obs._trazador is not None
    with obs.span("test_span", {"clave": "valor"}) as span:
        assert span is not None


# ---------------- StateMachine ----------------

def test_max_iteraciones_valor():
    assert MAX_ITERACIONES == 6


def test_auditor_harness_instancia():
    harness = AuditorHarness()
    assert harness is not None
    assert harness._grafo is not None


# ---------------- Evals Suite ----------------

def test_evals_tool_selection_accuracy():
    suite = EvalsSuite()
    assert suite.tool_selection_accuracy(["get_git_diff"], ["get_git_diff"]) == 1.0
    assert suite.tool_selection_accuracy(["get_git_diff"], ["read_source_file"]) == 0.0
    assert suite.tool_selection_accuracy([], []) == 1.0


def test_evals_context_precision():
    suite = EvalsSuite()
    assert suite.context_precision(3, 5) == 0.6
    assert suite.context_precision(0, 0) == 0.0


def test_evals_context_recall():
    suite = EvalsSuite()
    assert suite.context_recall(3, 10) == 0.3
    assert suite.context_recall(0, 0) == 0.0


def test_evals_ejecutar_gate_aprueba():
    suite = EvalsSuite()
    resp = AuditorResponse(
        hallazgos=[],
        resumen=ResumenHallazgos(total=0),
        citas_rag=["OWASP A03"],
    )
    resultado = suite.ejecutar_gate(resp, ["OWASP A03"])
    assert isinstance(resultado, ValidacionResultado)


def test_evals_ejecutar_gate_rechaza():
    suite = EvalsSuite()
    resp = {"hallazgos": "no_valido"}
    resultado = suite.ejecutar_gate(resp, [])
    assert resultado.aprobado is False


# ---------------- MCP Server ----------------

def test_register_tool_agrega_herramienta():
    llamadas = []

    def handler(arg):
        llamadas.append(arg)
        return {"exito": True}

    register_tool(
        name="test_tool_extra",
        description="tool de prueba",
        input_schema={"type": "object"},
        handler=handler,
    )
    assert "test_tool_extra" in _TOOLS


# ---------------- get_git_diff ----------------

def test_get_git_diff_staged_exitoso(monkeypatch):
    import mcp_server.tools.get_git_diff as mod

    class FakeGit:
        def diff(self, *args, **kwargs):
            return "diff contenido staged"

    class FakeRepo:
        def __init__(self, path):
            self.path = path
            self.git = FakeGit()

    monkeypatch.setattr(mod, "Repo", FakeRepo)
    resultado = get_git_diff({"ruta_repo": "/tmp/fake", "staged": True})
    assert resultado["exito"] is True
    assert resultado["datos"]["diff"] == "diff contenido staged"


def test_get_git_diff_con_rango_commits(monkeypatch):
    import mcp_server.tools.get_git_diff as mod

    class FakeGit:
        def diff(self, *args, **kwargs):
            return "diff rango"

    class FakeRepo:
        def __init__(self, path):
            self.path = path
            self.git = FakeGit()

    monkeypatch.setattr(mod, "Repo", FakeRepo)
    resultado = get_git_diff({"ruta_repo": "/tmp/fake", "commit_range": "HEAD~1..HEAD"})
    assert resultado["exito"] is True
    assert resultado["datos"]["commit_range"] == "HEAD~1..HEAD"


# ---------------- run_static_analysis ----------------

def test_run_static_analysis_con_linter_mockeado(monkeypatch):
    import mcp_server.tools.run_static_analysis as mod

    monkeypatch.setattr(mod.shutil, "which", lambda x: "ruff")

    class FakeResult:
        returncode = 0
        stdout = '[{"archivo": "test.py", "mensaje": "ok"}]'
        stderr = ""

    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: FakeResult())
    resultado = run_static_analysis({"ruta_archivo": "test.py"})
    assert resultado["exito"] is True
    assert len(resultado["datos"]["diagnosticos"]) == 1


def test_run_static_analysis_timeout(monkeypatch):
    import mcp_server.tools.run_static_analysis as mod

    monkeypatch.setattr(mod.shutil, "which", lambda x: "ruff")

    def timeout_run(*a, **k):
        raise mod.subprocess.TimeoutExpired("cmd", 60)

    monkeypatch.setattr(mod.subprocess, "run", timeout_run)
    resultado = run_static_analysis({"ruta_archivo": "test.py"})
    assert resultado["exito"] is False
    assert "Tiempo de espera" in resultado["error"]


# ---------------- PerfilStore ----------------

def test_perfil_store_cargar_inexistente(tmp_path):
    db = tmp_path / "perfiles.db"
    store = PerfilStore(str(db))
    assert store.cargar_perfil("noexiste") is None
    store.cerrar()


def test_perfil_store_guardar_tripla_y_listar(tmp_path):
    db = tmp_path / "perfiles.db"
    store = PerfilStore(str(db))
    tripla = TriplaSemantica(sujeto="usuario", predicado="prefiere_framework", objeto="django")
    store.guardar_tripla("u1", tripla)
    triplas = store.listar_triplas("u1")
    assert len(triplas) == 1
    assert triplas[0]["sujeto"] == "usuario"
    store.cerrar()


def test_extractor_hechos_sin_coincidencias():
    extractor = ExtractorHechos()
    triplas = extractor.extraer("texto sin palabras clave")
    assert triplas == []


# ---------------- Chunking ----------------

def test_chunking_texto_corto_un_chunk():
    pipeline = ChunkingPipeline(chunk_size=500, chunk_overlap=50)
    chunks = pipeline.chunk_documento("texto corto", {"fuente": "x.md"})
    assert len(chunks) == 1


def test_chunking_metadata_por_defecto():
    pipeline = ChunkingPipeline()
    chunks = pipeline.chunk_documento("texto de prueba para chunking")
    for c in chunks:
        assert "metadata" in c
        assert "texto" in c
        assert "token_count" in c


# ---------------- Retriever ----------------

def test_retriever_sin_documentos():
    retriever = RagRetriever(umbral=0.72)
    resultado = retriever.recuperar("consulta cualquiera")
    assert resultado["umbral_alcanzado"] is False
    assert resultado["documentos"] == []
    assert resultado["citas"] == []


def test_embedding_model_fallback():
    modelo = EmbeddingModel(modelo="modelo_inexistente")
    emb = modelo.embed("texto de prueba")
    assert isinstance(emb, list)
    assert len(emb) == 384


# ---------------- VectorStore ----------------

def test_vector_store_config_valores_por_defecto():
    config = VectorStoreConfig()
    assert config.provider == "chromadb"
    assert config.similarity_threshold == 0.72
    assert config.collection_name == "dsia_directrices"


def test_vector_store_proveedor_no_soportado():
    config = VectorStoreConfig()
    config.provider = "inexistente"
    store = VectorStore(config)
    with pytest.raises(ValueError):
        store._ensure_client()


# ---------------- AST File Inspector ----------------

def test_ast_file_inspector_valido(tmp_path):
    archivo = tmp_path / "ejemplo.py"
    archivo.write_text(
        '"""Modulo de ejemplo"""\n'
        "import os\n"
        "from sys import path\n"
        "\n"
        "class MiClase:\n"
        "    \"\"\"Docstring de clase.\"\"\"\n"
        "\n"
        "    def metodo(self, x):\n"
        "        if x > 0:\n"
        "            return x\n"
        "        else:\n"
        "            return 0\n"
        "\n"
        "def funcion_global(a, b):\n"
        "    try:\n"
        "        return a + b\n"
        "    except Exception:\n"
        "        return None\n"
    )

    resultado = ast_file_inspector({"ruta_archivo": str(archivo)})
    assert resultado["exito"] is True
    datos = resultado["datos"]
    assert datos["clases"] == 1
    assert datos["funciones"] == 2  # metodo + funcion_global
    assert datos["imports"] == 2
    assert datos["complejidad_ciclomatica"] >= 3
    assert datos["docstring_modulo"] == "Modulo de ejemplo"


def test_ast_file_inspector_archivo_inexistente():
    resultado = ast_file_inspector({"ruta_archivo": "/no/existe.py"})
    assert resultado["exito"] is False
    assert "error" in resultado


def test_ast_file_inspector_error_sintaxis(tmp_path):
    archivo = tmp_path / "malo.py"
    archivo.write_text("def foo(:\n    pass\n")
    resultado = ast_file_inspector({"ruta_archivo": str(archivo)})
    assert resultado["exito"] is False
    assert "Error de sintaxis" in resultado["error"]


def test_ast_file_inspector_sin_ruta():
    resultado = ast_file_inspector({})
    assert resultado["exito"] is False
    assert "ruta_archivo es requerido" in resultado["error"]
