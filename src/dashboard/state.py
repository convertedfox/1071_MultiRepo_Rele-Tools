from __future__ import annotations

from enum import StrEnum
from typing import Any


class WorkflowStep(StrEnum):
    PDF_1049 = "pdf_1049"
    RELE_1067 = "rele_1067"
    IMPORT_1052 = "import_1052"


KEY_STEP_1049_DONE = "step_1049_done"
KEY_STEP_1067_DONE = "step_1067_done"
KEY_STEP_1052_DONE = "step_1052_done"

KEY_1049_DATAFRAME = "tool_1049_dataframe"
KEY_1049_EXPORT_BYTES = "tool_1049_export_bytes"
KEY_1049_EXPORT_NAME = "tool_1049_export_name"

KEY_1067_DATAFRAME = "tool_1067_dataframe"
KEY_1067_CSV_BYTES = "tool_1067_csv_bytes"
KEY_1067_XLSX_BYTES = "tool_1067_xlsx_bytes"
KEY_1067_CSV_NAME = "tool_1067_csv_name"
KEY_1067_XLSX_NAME = "tool_1067_xlsx_name"

KEY_1052_UPLOAD_SIGNATURE = "tool_1052_upload_signature"
KEY_1052_VALIDATION = "tool_1052_validation"
KEY_1052_VALIDATION_ERROR = "tool_1052_validation_error"
KEY_1052_TRANSFORM_ERROR = "tool_1052_transform_error"
KEY_1052_OUTPUT_BYTES = "tool_1052_output_bytes"
KEY_1052_OUTPUT_NAME = "tool_1052_output_name"
KEY_1052_BESOLDUNG_DATE = "tool_1052_besoldung_date"
KEY_1052_REST_DATE = "tool_1052_rest_date"

_STEP_TO_KEY = {
    WorkflowStep.PDF_1049: KEY_STEP_1049_DONE,
    WorkflowStep.RELE_1067: KEY_STEP_1067_DONE,
    WorkflowStep.IMPORT_1052: KEY_STEP_1052_DONE,
}

_STEP_TO_LABEL = {
    WorkflowStep.PDF_1049: "PDF-Extraktor",
    WorkflowStep.RELE_1067: "RELElisten-Extraktor",
    WorkflowStep.IMPORT_1052: "Buchungsimporteur",
}

_DEFAULTS: dict[str, Any] = {
    KEY_STEP_1049_DONE: False,
    KEY_STEP_1067_DONE: False,
    KEY_STEP_1052_DONE: False,
    KEY_1049_DATAFRAME: None,
    KEY_1049_EXPORT_BYTES: None,
    KEY_1049_EXPORT_NAME: None,
    KEY_1067_DATAFRAME: None,
    KEY_1067_CSV_BYTES: None,
    KEY_1067_XLSX_BYTES: None,
    KEY_1067_CSV_NAME: None,
    KEY_1067_XLSX_NAME: None,
    KEY_1052_UPLOAD_SIGNATURE: None,
    KEY_1052_VALIDATION: None,
    KEY_1052_VALIDATION_ERROR: None,
    KEY_1052_TRANSFORM_ERROR: None,
    KEY_1052_OUTPUT_BYTES: None,
    KEY_1052_OUTPUT_NAME: None,
    KEY_1052_BESOLDUNG_DATE: None,
    KEY_1052_REST_DATE: None,
}


def init_state(store: Any) -> None:
    for key, default_value in _DEFAULTS.items():
        store.setdefault(key, default_value)


def mark_step_completed(store: Any, step: WorkflowStep) -> None:
    store[_STEP_TO_KEY[step]] = True


def is_step_completed(store: Any, step: WorkflowStep) -> bool:
    return bool(store.get(_STEP_TO_KEY[step], False))


def workflow_overview(store: Any) -> list[tuple[WorkflowStep, str, bool]]:
    return [
        (step, _STEP_TO_LABEL[step], is_step_completed(store, step))
        for step in WorkflowStep
    ]
