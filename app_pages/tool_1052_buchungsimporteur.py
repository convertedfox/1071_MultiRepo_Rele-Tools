from __future__ import annotations

import hashlib
from datetime import date

import streamlit as st

from dashboard.integrations.base import ToolIntegrationError
from dashboard.integrations.tool_1052_adapter import (
    compute_default_booking_dates,
    get_required_source_columns,
    transform_input_excel,
    validate_input_excel,
)
from dashboard.state import (
    KEY_1052_BESOLDUNG_DATE,
    KEY_1052_OUTPUT_BYTES,
    KEY_1052_OUTPUT_NAME,
    KEY_1052_REST_DATE,
    KEY_1052_TRANSFORM_ERROR,
    KEY_1052_UPLOAD_SIGNATURE,
    KEY_1052_VALIDATION,
    KEY_1052_VALIDATION_ERROR,
    WorkflowStep,
    init_state,
    mark_step_completed,
)

init_state(st.session_state)

st.subheader("Schritt 3: SAP LBV Buchungsimport erzeugen")
input_file = st.file_uploader("Eingabe-Excel", type=["xlsx", "xls"])

if input_file is None:
    st.info("Bitte eine Eingabe-Excel hochladen.")
    st.stop()

payload = input_file.getvalue()
signature = (input_file.name, len(payload), hashlib.sha256(payload).hexdigest())

if st.session_state.get(KEY_1052_UPLOAD_SIGNATURE) != signature:
    try:
        default_besoldung, default_rest = compute_default_booking_dates()
    except ToolIntegrationError as exc:
        st.error(str(exc))
        st.stop()

    st.session_state[KEY_1052_UPLOAD_SIGNATURE] = signature
    st.session_state[KEY_1052_BESOLDUNG_DATE] = default_besoldung
    st.session_state[KEY_1052_REST_DATE] = default_rest
    st.session_state[KEY_1052_VALIDATION] = None
    st.session_state[KEY_1052_VALIDATION_ERROR] = None
    st.session_state[KEY_1052_OUTPUT_BYTES] = None
    st.session_state[KEY_1052_OUTPUT_NAME] = None
    st.session_state[KEY_1052_TRANSFORM_ERROR] = None

try:
    required_columns = get_required_source_columns()
except ToolIntegrationError as exc:
    st.error(str(exc))
    st.stop()

with st.expander("Pflichtspalten", expanded=True):
    for col in required_columns:
        st.write(f"- {col}")

if st.button("Eingabe pruefen", use_container_width=True):
    try:
        details = validate_input_excel(input_file.name, payload)
    except ToolIntegrationError as exc:
        st.session_state[KEY_1052_VALIDATION_ERROR] = str(exc)
        st.session_state[KEY_1052_VALIDATION] = None
    else:
        st.session_state[KEY_1052_VALIDATION] = details
        st.session_state[KEY_1052_VALIDATION_ERROR] = None

validation_error = st.session_state.get(KEY_1052_VALIDATION_ERROR)
if isinstance(validation_error, str) and validation_error:
    st.error(validation_error)

validation = st.session_state.get(KEY_1052_VALIDATION)
if validation is not None:
    st.success(
        f"Validierung erfolgreich. Zeilen: {validation.rows} | "
        f"Spalten: {validation.columns}"
    )
    with st.expander("Validierungsdetails", expanded=False):
        if validation.mapping:
            st.json(validation.mapping)
        st.dataframe(validation.preview, use_container_width=True, hide_index=True)

default_output_name = f"SAP_LBV_Import_{date.today().strftime('%Y-%m-%d')}.xlsx"
with st.form("transform_form", border=True):
    left, right = st.columns(2)
    with left:
        st.date_input(
            "Buchungsdatum Besoldung",
            key=KEY_1052_BESOLDUNG_DATE,
            format="DD.MM.YYYY",
        )
    with right:
        st.date_input(
            "Buchungsdatum Rest",
            key=KEY_1052_REST_DATE,
            format="DD.MM.YYYY",
        )

    output_name = st.text_input("Ausgabedateiname", value=default_output_name)
    submit_transform = st.form_submit_button(
        "Transformation starten",
        use_container_width=True,
    )

if submit_transform:
    try:
        artifact = transform_input_excel(
            upload_name=input_file.name,
            payload=payload,
            output_name=output_name,
            besoldung_date=st.session_state[KEY_1052_BESOLDUNG_DATE],
            rest_date=st.session_state[KEY_1052_REST_DATE],
        )
    except ToolIntegrationError as exc:
        st.session_state[KEY_1052_TRANSFORM_ERROR] = str(exc)
        st.session_state[KEY_1052_OUTPUT_BYTES] = None
        st.session_state[KEY_1052_OUTPUT_NAME] = None
    else:
        st.session_state[KEY_1052_TRANSFORM_ERROR] = None
        st.session_state[KEY_1052_OUTPUT_BYTES] = artifact.payload
        st.session_state[KEY_1052_OUTPUT_NAME] = artifact.file_name
        mark_step_completed(st.session_state, WorkflowStep.IMPORT_1052)

transform_error = st.session_state.get(KEY_1052_TRANSFORM_ERROR)
if isinstance(transform_error, str) and transform_error:
    st.error(transform_error)

output_bytes = st.session_state.get(KEY_1052_OUTPUT_BYTES)
output_file_name = st.session_state.get(KEY_1052_OUTPUT_NAME)
if isinstance(output_bytes, bytes) and isinstance(output_file_name, str):
    st.success("Transformation abgeschlossen")
    st.download_button(
        "Ausgabe herunterladen",
        data=output_bytes,
        file_name=output_file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
