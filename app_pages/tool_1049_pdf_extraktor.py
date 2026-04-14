from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.integrations.base import ToolIntegrationError
from dashboard.integrations.tool_1049_adapter import extract_zip_payload
from dashboard.state import (
    KEY_1049_DATAFRAME,
    KEY_1049_EXPORT_BYTES,
    KEY_1049_EXPORT_NAME,
    WorkflowStep,
    init_state,
    mark_step_completed,
)

init_state(st.session_state)

st.subheader("Schritt 1: ZIP mit PDF-Dateien auswerten")
uploaded_zip = st.file_uploader("ZIP-Datei hochladen", type=["zip"])

if uploaded_zip is not None and st.button(
    "Extraktion starten", use_container_width=True
):
    with st.spinner("1049-Extraktion laeuft..."):
        try:
            result = extract_zip_payload(uploaded_zip)
        except ToolIntegrationError as exc:
            st.error(str(exc))
        else:
            st.session_state[KEY_1049_DATAFRAME] = result.dataframe
            st.session_state[KEY_1049_EXPORT_BYTES] = result.excel_artifact.payload
            st.session_state[KEY_1049_EXPORT_NAME] = result.excel_artifact.file_name
            mark_step_completed(st.session_state, WorkflowStep.PDF_1049)
            st.success(f"Extraktion erfolgreich: {len(result.dataframe)} Positionen.")

dataframe: pd.DataFrame | None = st.session_state.get(KEY_1049_DATAFRAME)
if isinstance(dataframe, pd.DataFrame) and not dataframe.empty:
    st.subheader("Vorschau")
    st.dataframe(dataframe, use_container_width=True, hide_index=True)

    st.subheader("Kurzstatistik")
    total_amount = (
        dataframe["Betrag (€)"].sum() if "Betrag (€)" in dataframe.columns else 0
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Positionen", value=len(dataframe))
    c2.metric("Dateien", value=int(dataframe["Quelldatei"].nunique()))
    c3.metric("Summe", value=f"{total_amount:,.2f} EUR")

export_bytes = st.session_state.get(KEY_1049_EXPORT_BYTES)
export_name = st.session_state.get(KEY_1049_EXPORT_NAME)
if isinstance(export_bytes, bytes) and isinstance(export_name, str):
    st.download_button(
        "Excel herunterladen",
        data=export_bytes,
        file_name=export_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
