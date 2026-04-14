from __future__ import annotations

import streamlit as st

from dashboard.state import init_state
from dashboard.ui import render_hero

init_state(st.session_state)

render_hero(
    title="Willkommen in der Rele-Toolbox 🛠️",
    description=(
        "Diese Anwendung bündelt die RELE-Werkzeuge. "
        "Sie können jedes Tool direkt auswählen."
    ),
)

st.subheader("Toolübersicht")
left, middle, right = st.columns(3, vertical_alignment="top")
with left:
    with st.container(border=True):
        st.markdown("**PDF-Extraktor**")
        st.caption(
            "Extrahiert Positionen aus PDF-Bündeln und erzeugt eine Excel-Ausgabe."
        )
        st.page_link(
            "app_pages/tool_1049_pdf_extraktor.py",
            label="Tool oeffnen",
            use_container_width=True,
        )
with middle:
    with st.container(border=True):
        st.markdown("**RELE-Listen-Extraktor**")
        st.caption(
            "Liest RELE-PDF-Dateien aus und exportiert strukturierte Abrechnungsdaten."
        )
        st.page_link(
            "app_pages/tool_1067_relelisten_extraktor.py",
            label="Tool oeffnen",
            use_container_width=True,
        )
with right:
    with st.container(border=True):
        st.markdown("**Buchungsimporteur**")
        st.caption("Validiert Eingaben und erzeugt die finale SAP-LBV-Importdatei.")
        st.page_link(
            "app_pages/tool_1052_buchungsimporteur.py",
            label="Tool oeffnen",
            use_container_width=True,
        )

st.caption(
    "Diese Anwendung enthält nur Orchestrierung "
    "und Bedienoberfläche. "
    "Die Fachlogik bleibt in den jeweiligen Einzel-Repos."
)
