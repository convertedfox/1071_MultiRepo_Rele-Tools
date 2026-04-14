from __future__ import annotations

from dataclasses import dataclass

import pytest

from dashboard.upload_validation import (
    MAX_1049_ZIP_BYTES,
    MAX_1052_EXCEL_BYTES,
    MAX_1067_FILE_BYTES,
    MAX_1067_FILES,
    MAX_1067_TOTAL_BYTES,
    UploadValidationError,
    validate_1049_zip_upload,
    validate_1052_excel_upload,
    validate_1067_uploads,
)


@dataclass(slots=True)
class DummyUpload:
    name: str
    size: int

    def getvalue(self) -> bytes:
        return b"x" * self.size


def test_validate_1049_zip_upload_accepts_valid_file() -> None:
    uploaded = DummyUpload(name="daten.zip", size=1024)

    info = validate_1049_zip_upload(uploaded)

    assert info.name == "daten.zip"
    assert info.size_bytes == 1024


def test_validate_1049_zip_upload_rejects_large_file() -> None:
    uploaded = DummyUpload(name="daten.zip", size=MAX_1049_ZIP_BYTES + 1)

    with pytest.raises(UploadValidationError):
        validate_1049_zip_upload(uploaded)


def test_validate_1052_excel_upload_rejects_wrong_extension() -> None:
    uploaded = DummyUpload(name="daten.csv", size=100)

    with pytest.raises(UploadValidationError):
        validate_1052_excel_upload(uploaded)


def test_validate_1052_excel_upload_rejects_large_file() -> None:
    uploaded = DummyUpload(name="daten.xlsx", size=MAX_1052_EXCEL_BYTES + 1)

    with pytest.raises(UploadValidationError):
        validate_1052_excel_upload(uploaded)


def test_validate_1067_uploads_rejects_too_many_files() -> None:
    uploads = [
        DummyUpload(name=f"{idx}.pdf", size=100) for idx in range(MAX_1067_FILES + 1)
    ]

    with pytest.raises(UploadValidationError):
        validate_1067_uploads(uploads)


def test_validate_1067_uploads_rejects_single_file_size_limit() -> None:
    uploads = [DummyUpload(name="daten.pdf", size=MAX_1067_FILE_BYTES + 1)]

    with pytest.raises(UploadValidationError):
        validate_1067_uploads(uploads)


def test_validate_1067_uploads_rejects_total_size_limit() -> None:
    half = MAX_1067_TOTAL_BYTES // 2 + 1
    uploads = [
        DummyUpload(name="teil1.pdf", size=half),
        DummyUpload(name="teil2.pdf", size=half),
    ]

    with pytest.raises(UploadValidationError):
        validate_1067_uploads(uploads)
