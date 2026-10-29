"""Herramienta MCP: get_git_diff (T2).

Obtiene cambios staged o de un rango de commits usando GitPython.
"""

from __future__ import annotations

from typing import Any

from git import InvalidGitRepositoryError, Repo


def get_git_diff(arguments: dict[str, Any]) -> dict[str, Any]:
    """Retorna el diff staged o de un rango de commits."""
    repo_path = arguments.get("ruta_repo", ".")
    staged = arguments.get("staged", True)
    commit_range = arguments.get("commit_range")

    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        return {"exito": False, "error": f"No es un repositorio git: {repo_path}", "datos": {}}

    try:
        if commit_range:
            diff = repo.git.diff(commit_range)
        elif staged:
            diff = repo.git.diff("--cached")
        else:
            diff = repo.git.diff()
        return {"exito": True, "datos": {"diff": diff, "staged": staged, "commit_range": commit_range}}
    except Exception as exc:  # noqa: BLE001
        return {"exito": False, "error": str(exc), "datos": {}}
