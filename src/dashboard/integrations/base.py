from __future__ import annotations

import sys
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


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
TOOLS_ROOT = WORKSPACE_ROOT / "tools"

_TOOL_DIRECTORY_NAMES = {
    ToolKey.PDF_1049: "1049-pdf-extraktor-lbv",
    ToolKey.RELE_1067: "1067-relelisten-extraktor",
    ToolKey.IMPORT_1052: "1052-buchungsimporteur-sap-lbv",
}


def resolve_tool_root(tool: ToolKey | str, workspace_root: Path | None = None) -> Path:
    try:
        tool_key = ToolKey(tool)
    except ValueError as exc:
        raise ToolIntegrationError(f"Unbekannter Tool-Schluessel: {tool}") from exc

    root = workspace_root or WORKSPACE_ROOT
    return root / "tools" / _TOOL_DIRECTORY_NAMES[tool_key]


def register_tool_import_paths(
    tool: ToolKey | str, workspace_root: Path | None = None
) -> Path:
    tool_root = resolve_tool_root(tool, workspace_root=workspace_root)
    if not tool_root.exists():
        raise ToolIntegrationError(
            "Tool-Verzeichnis nicht gefunden: "
            f"{tool_root}. Bitte Submodule initialisieren."
        )

    tool_key = ToolKey(tool)
    candidates: list[Path]
    if tool_key == ToolKey.IMPORT_1052:
        src_path = tool_root / "src"
        if not src_path.exists():
            raise ToolIntegrationError(
                f"Erwartetes src-Verzeichnis fehlt fuer 1052: {src_path}"
            )
        candidates = [src_path, tool_root]
    else:
        candidates = [tool_root]

    for path in reversed(candidates):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

    return tool_root
