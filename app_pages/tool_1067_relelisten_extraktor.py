from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.integrations.base import ToolIntegrationError
from dashboard.integrations.tool_1067_adapter import (
    build_rele_exports,
    extract_rele_documents,
)
from dashboard.state import (
    KEY_1067_CSV_BYTES,
    KEY_1067_CSV_NAME,
    KEY_1067_DATAFRAME,
    KEY_1067_XLSX_BYTES,
    KEY_1067_XLSX_NAME,
    init_state,
)
from dashboard.ui import render_hero
from dashboard.upload_validation import UploadValidationError, validate_1067_uploads

init_state(st.session_state)

render_hero(
    title="RELE-Listen-Extraktion",
    description=(
        "Dieser Schritt extrahiert strukturierte RELE-Daten aus PDF-Dateien "
        "und stellt CSV- sowie Excel-Exporte bereit."
    ),
)

with st.container(border=True):
    st.markdown("**Eingabe**")
    uploads = st.file_uploader(
        "PDF-Dateien oder ZIP-Bündel hochladen",
        type=["pdf", "zip"],
        accept_multiple_files=True,
    )
    st.caption(
        "Mehrfachauswahl ist erlaubt. ZIP-Dateien können Unterordner enthalten. "
        "Maximal 50 Dateien, 30 MB je Datei, 300 MB gesamt."
    )

if uploads and st.button("RELE-Extraktion starten", use_container_width=True):
    with st.spinner("Die Extraktion wird ausgeführt..."):
        try:
            validate_1067_uploads(uploads)
            result = extract_rele_documents(uploads)
            suffix = (
                str(result.dataframe["Abrechnungsmonat/Jahr"].iloc[0])
                if not result.dataframe.empty
                else "export"
            )
            csv_artifact, xlsx_artifact = build_rele_exports(result.dataframe, suffix)
        except (ToolIntegrationError, UploadValidationError) as exc:
            st.error(str(exc))
        else:
            st.session_state[KEY_1067_DATAFRAME] = result.dataframe
            st.session_state[KEY_1067_CSV_BYTES] = csv_artifact.payload
            st.session_state[KEY_1067_CSV_NAME] = csv_artifact.file_name
            st.session_state[KEY_1067_XLSX_BYTES] = xlsx_artifact.payload
            st.session_state[KEY_1067_XLSX_NAME] = xlsx_artifact.file_name
            st.success(
                f"Extraktion erfolgreich: {len(result.dataframe)} Datensätze "
                f"aus {result.documents_count} Dokument(en)."
            )

dataframe: pd.DataFrame | None = st.session_state.get(KEY_1067_DATAFRAME)
if isinstance(dataframe, pd.DataFrame) and not dataframe.empty:
    st.metric("Datensätze", value=len(dataframe))

    summary = dataframe.groupby("Buchungsstelle", as_index=False).agg(
        Anzahl=("Personalnummer", "count")
    )
    summary = summary.sort_values("Buchungsstelle")

    tab_daten, tab_statistik = st.tabs(["Datenvorschau", "Kurzstatistik"])
    with tab_daten:
        st.dataframe(dataframe, use_container_width=True, hide_index=True)
    with tab_statistik:
        st.dataframe(summary, use_container_width=True, hide_index=True)

csv_bytes = st.session_state.get(KEY_1067_CSV_BYTES)
csv_name = st.session_state.get(KEY_1067_CSV_NAME)
xlsx_bytes = st.session_state.get(KEY_1067_XLSX_BYTES)
xlsx_name = st.session_state.get(KEY_1067_XLSX_NAME)

if any(
    [
        isinstance(csv_bytes, bytes) and isinstance(csv_name, str),
        isinstance(xlsx_bytes, bytes) and isinstance(xlsx_name, str),
    ]
):
    with st.container(border=True):
        st.markdown("**Export**")
        left, right = st.columns(2)
        with left:
            if isinstance(csv_bytes, bytes) and isinstance(csv_name, str):
                st.download_button(
                    "CSV herunterladen",
                    data=csv_bytes,
                    file_name=csv_name,
                    mime="text/csv",
                    use_container_width=True,
                )
        with right:
            if isinstance(xlsx_bytes, bytes) and isinstance(xlsx_name, str):
                st.download_button(
                    "Excel herunterladen",
                    data=xlsx_bytes,
                    file_name=xlsx_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
