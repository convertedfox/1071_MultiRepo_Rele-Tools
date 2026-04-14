from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

MB = 1024 * 1024

MAX_1049_ZIP_BYTES = 200 * MB
MAX_1067_FILES = 50
MAX_1067_FILE_BYTES = 30 * MB
MAX_1067_TOTAL_BYTES = 300 * MB
MAX_1052_EXCEL_BYTES = 30 * MB


class UploadValidationError(ValueError):
    """Fehler bei der Vorabvalidierung von Uploads."""


@dataclass(slots=True, frozen=True)
class UploadInfo:
    name: str
    size_bytes: int


def validate_1049_zip_upload(uploaded_file: Any) -> UploadInfo:
    return validate_single_upload(
        uploaded_file=uploaded_file,
        allowed_extensions={".zip"},
        max_size_bytes=MAX_1049_ZIP_BYTES,
        context="1049 PDF-Extraktion",
    )


def validate_1052_excel_upload(uploaded_file: Any) -> UploadInfo:
    return validate_single_upload(
        uploaded_file=uploaded_file,
        allowed_extensions={".xlsx", ".xls"},
        max_size_bytes=MAX_1052_EXCEL_BYTES,
        context="1052 Buchungsimport",
    )


def validate_1067_uploads(uploaded_files: list[Any]) -> list[UploadInfo]:
    file_count = len(uploaded_files)
    if file_count == 0:
        raise UploadValidationError("Bitte mindestens eine Datei hochladen.")
    if file_count > MAX_1067_FILES:
        raise UploadValidationError(
            f"Zu viele Dateien für 1067. Erlaubt sind maximal {MAX_1067_FILES} Dateien."
        )

    infos = [
        validate_single_upload(
            uploaded_file=uploaded_file,
            allowed_extensions={".pdf", ".zip"},
            max_size_bytes=MAX_1067_FILE_BYTES,
            context="1067 RELE-Extraktion",
        )
        for uploaded_file in uploaded_files
    ]

    total_size = sum(info.size_bytes for info in infos)
    if total_size > MAX_1067_TOTAL_BYTES:
        raise UploadValidationError(
            "Die Gesamtgröße der Uploads ist zu hoch für 1067 "
            f"({format_mebibytes(total_size)} MB). "
            f"Erlaubt sind maximal {format_mebibytes(MAX_1067_TOTAL_BYTES)} MB."
        )

    return infos


def validate_single_upload(
    uploaded_file: Any,
    allowed_extensions: set[str],
    max_size_bytes: int,
    context: str,
) -> UploadInfo:
    if uploaded_file is None:
        raise UploadValidationError(f"Bitte eine Datei für {context} hochladen.")

    name = str(getattr(uploaded_file, "name", "")).strip()
    if not name:
        raise UploadValidationError(f"Der Dateiname für {context} fehlt.")

    extension = Path(name).suffix.lower()
    if extension not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise UploadValidationError(
            f"Ungültiger Dateityp für {context}: {name}. Erlaubt sind: {allowed}."
        )

    size_bytes = read_upload_size_bytes(uploaded_file)
    if size_bytes > max_size_bytes:
        raise UploadValidationError(
            f"Datei zu groß für {context}: {name} "
            f"({format_mebibytes(size_bytes)} MB). "
            f"Erlaubt sind maximal {format_mebibytes(max_size_bytes)} MB."
        )

    return UploadInfo(name=name, size_bytes=size_bytes)


def read_upload_size_bytes(uploaded_file: Any) -> int:
    size = getattr(uploaded_file, "size", None)
    if isinstance(size, int) and size >= 0:
        return size
    payload = uploaded_file.getvalue()
    if not isinstance(payload, bytes):
        raise UploadValidationError("Hochgeladene Datei konnte nicht gelesen werden.")
    return len(payload)


def format_mebibytes(size_bytes: int) -> str:
    return f"{size_bytes / MB:.1f}"
