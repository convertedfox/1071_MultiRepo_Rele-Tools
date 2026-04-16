from __future__ import annotations

import importlib
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class ToolIntegrationError(RuntimeError):
    """Fehler bei der Integration eines Tool-Submoduls."""


class ToolKey(StrEnum):
    PDF_1049 = "1049"
    RELE_1067 = "1067"
    IMPORT_1052 = "1052"


@dataclass(slots=True, frozen=True)
class BinaryArtifact:
    file_name: str
    payload: bytes
    mime_type: str


@dataclass(slots=True, frozen=True)
class ToolDiagnostic:
    tool: ToolKey
    display_name: str
    path: Path
    submodule_available: bool
    import_available: bool
    detail: str


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
TOOLS_ROOT = WORKSPACE_ROOT / "tools"
CACHE_ROOT = Path(tempfile.gettempdir()) / "rele-tool-cache"
CACHE_ROOT.mkdir(parents=True, exist_ok=True)

_TOOL_DIRECTORY_NAMES = {
    ToolKey.PDF_1049: "1049-pdf-extraktor-lbv",
    ToolKey.RELE_1067: "1067-relelisten-extraktor",
    ToolKey.IMPORT_1052: "1052-buchungsimporteur-sap-lbv",
}

_TOOL_DISPLAY_NAMES = {
    ToolKey.PDF_1049: "1049 PDF-Extraktor",
    ToolKey.RELE_1067: "1067 RELElisten-Extraktor",
    ToolKey.IMPORT_1052: "1052 Buchungsimporteur",
}

_TOOL_MODULE_NAMES = {
    ToolKey.PDF_1049: "main",
    ToolKey.RELE_1067: "relelisten_extraktor",
    ToolKey.IMPORT_1052: "buchungsimporteur",
}

_TOOL_GIT_URLS = {
    ToolKey.PDF_1049: "https://github.com/convertedfox/1049---PDF-Extraktor-LBV.git",
    ToolKey.RELE_1067: "https://github.com/convertedfox/RELEListen-Extraktor.git",
    ToolKey.IMPORT_1052: "https://github.com/convertedfox/1052---Buchungsimporteur-SAP-LBV.git",
}

_TOOL_SOURCE_HITS: dict[ToolKey, str] = {}


def resolve_tool_root(tool: ToolKey | str, workspace_root: Path | None = None) -> Path:
    try:
        tool_key = ToolKey(tool)
    except ValueError as exc:
        raise ToolIntegrationError(f"Unbekannter Tool-Schlüssel: {tool}") from exc

    root = workspace_root or WORKSPACE_ROOT
    return root / "tools" / _TOOL_DIRECTORY_NAMES[tool_key]


def register_tool_import_paths(
    tool: ToolKey | str, workspace_root: Path | None = None
) -> Path:
    tool_root = resolve_tool_root(tool, workspace_root=workspace_root)
    tool_key = ToolKey(tool)
    active_root = _ensure_tool_available(tool_key, tool_root, workspace_root)

    candidates: list[Path]
    if tool_key == ToolKey.IMPORT_1052:
        src_path = active_root / "src"
        if not src_path.exists():
            raise ToolIntegrationError(
                f"Erwartetes src-Verzeichnis fehlt für 1052: {src_path}"
            )
        candidates = [src_path, active_root]
    else:
        candidates = [active_root]

    for path in reversed(candidates):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

    return active_root


def collect_tool_diagnostics(
    workspace_root: Path | None = None,
) -> list[ToolDiagnostic]:
    return [
        diagnose_tool(tool_key, workspace_root=workspace_root) for tool_key in ToolKey
    ]


def diagnose_tool(
    tool: ToolKey,
    workspace_root: Path | None = None,
) -> ToolDiagnostic:
    tool_root = resolve_tool_root(tool, workspace_root=workspace_root)
    try:
        active_root = register_tool_import_paths(tool, workspace_root=workspace_root)
    except ToolIntegrationError as exc:
        return ToolDiagnostic(
            tool=tool,
            display_name=_TOOL_DISPLAY_NAMES[tool],
            path=tool_root,
            submodule_available=tool_root.exists(),
            import_available=False,
            detail=str(exc),
        )

    module_name = _TOOL_MODULE_NAMES[tool]
    try:
        importlib.import_module(module_name)
    except Exception as exc:
        return ToolDiagnostic(
            tool=tool,
            display_name=_TOOL_DISPLAY_NAMES[tool],
            path=active_root,
            submodule_available=True,
            import_available=False,
            detail=f"Import fehlgeschlagen: {exc}",
        )

    detail = "Bereit."
    if _TOOL_SOURCE_HITS.get(tool) == "cache":
        detail = "Bereit (Cache)"

    return ToolDiagnostic(
        tool=tool,
        display_name=_TOOL_DISPLAY_NAMES[tool],
        path=active_root,
        submodule_available=True,
        import_available=True,
        detail=detail,
    )


def _ensure_tool_available(
    tool: ToolKey, tool_root: Path, workspace_root: Path | None
) -> Path:
    if tool_root.exists():
        _TOOL_SOURCE_HITS[tool] = "local"
        return tool_root

    commit = _get_submodule_commit(tool, workspace_root=workspace_root)
    cache_dir = CACHE_ROOT / _TOOL_DIRECTORY_NAMES[tool] / commit
    if cache_dir.exists():
        _TOOL_SOURCE_HITS[tool] = "cache"
        return cache_dir

    repo_url = _TOOL_GIT_URLS[tool]
    tmp_dir = cache_dir.parent / f"tmp-{commit}"
    if tmp_dir.exists():
        subprocess.run(["rm", "-rf", str(tmp_dir)], check=False)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                repo_url,
                str(tmp_dir),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(tmp_dir), "checkout", commit],
            check=True,
            capture_output=True,
            text=True,
        )
        tmp_dir.rename(cache_dir)
    except subprocess.CalledProcessError as exc:
        error_text = exc.stderr.strip() if exc.stderr else str(exc)
        raise ToolIntegrationError(
            f"Tool-Repository konnte nicht geklont werden: {error_text}"
        ) from exc
    finally:
        if tmp_dir.exists() and not cache_dir.exists():
            subprocess.run(["rm", "-rf", str(tmp_dir)], check=False)

    _TOOL_SOURCE_HITS[tool] = "cache"
    return cache_dir


def _get_submodule_commit(tool: ToolKey, workspace_root: Path | None) -> str:
    relative_path = Path("tools") / _TOOL_DIRECTORY_NAMES[tool]
    cwd = workspace_root or WORKSPACE_ROOT
    try:
        output = subprocess.check_output(
            ["git", "ls-tree", "HEAD", str(relative_path)],
            cwd=str(cwd),
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise ToolIntegrationError(
            f"Konnte Submodul-Commit nicht bestimmen: {exc.stderr}"
        ) from exc

    parts = output.strip().split()
    if len(parts) < 3:
        raise ToolIntegrationError("Submodul-Commit konnte nicht gelesen werden.")
    return parts[2]
