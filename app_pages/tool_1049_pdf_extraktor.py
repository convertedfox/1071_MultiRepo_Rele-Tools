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
from dashboard.ui import render_hero

init_state(st.session_state)

render_hero(
    title="PDF-Extraktion (1049)",
    description=(
        "Lade ein ZIP-Buendel mit PDF-Dateien hoch. "
        "Die Anwendung extrahiert Positionen und erstellt eine Excel-Ausgabe."
    ),
)

with st.container(border=True):
    st.markdown("**Eingabe**")
    uploaded_zip = st.file_uploader("ZIP-Datei hochladen", type=["zip"])
    st.caption("Erlaubt sind ausschliesslich PDF-Dateien innerhalb des ZIP-Buendels.")

if uploaded_zip is not None and st.button(
    "Extraktion starten", use_container_width=True
):
    with st.spinner("Die 1049-Extraktion wird ausgefuehrt..."):
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
    total_amount = (
        dataframe["Betrag (€)"].sum() if "Betrag (€)" in dataframe.columns else 0
    )
    c1, c2, c3 = st.columns(3, vertical_alignment="center")
    c1.metric("Positionen", value=len(dataframe))
    c2.metric("Dateien", value=int(dataframe["Quelldatei"].nunique()))
    c3.metric("Gesamtsumme", value=f"{total_amount:,.2f} EUR")

    tab_daten, tab_auswertung = st.tabs(["Datenvorschau", "Auswertung"])
    with tab_daten:
        st.dataframe(dataframe, use_container_width=True, hide_index=True)
    with tab_auswertung:
        if "Standort" in dataframe.columns and "Betrag (€)" in dataframe.columns:
            standort_summary = (
                dataframe.groupby("Standort", as_index=False)["Betrag (€)"]
                .agg(["count", "sum"])
                .reset_index()
            )
            standort_summary.columns = [
                "Standort",
                "Anzahl Positionen",
                "Gesamtbetrag",
            ]
            st.dataframe(standort_summary, use_container_width=True, hide_index=True)
        else:
            st.caption("Keine Standortauswertung verfuegbar.")

export_bytes = st.session_state.get(KEY_1049_EXPORT_BYTES)
export_name = st.session_state.get(KEY_1049_EXPORT_NAME)
if isinstance(export_bytes, bytes) and isinstance(export_name, str):
    with st.container(border=True):
        st.markdown("**Export**")
        st.download_button(
            "Excel-Datei herunterladen",
            data=export_bytes,
            file_name=export_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
