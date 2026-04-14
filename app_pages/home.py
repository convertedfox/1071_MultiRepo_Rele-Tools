from __future__ import annotations

import streamlit as st

from dashboard.state import init_state, workflow_overview

init_state(st.session_state)

st.subheader("Willkommen")
st.write(
    "Dieses Dashboard fuehrt durch die Toolkette fuer RELE-/Personaldaten: "
    "1049 -> 1067 (optional) -> 1052."
)

st.subheader("Ablaufstatus")
for _, label, done in workflow_overview(st.session_state):
    icon = "[x]" if done else "[ ]"
    st.write(f"{icon} {label}")

st.divider()
st.subheader("Direkt zu den Tools")
left, middle, right = st.columns(3)
with left:
    st.page_link(
        "app_pages/tool_1049_pdf_extraktor.py",
        label="1049 PDF-Extraktor",
        icon=":material/picture_as_pdf:",
    )
with middle:
    st.page_link(
        "app_pages/tool_1067_relelisten_extraktor.py",
        label="1067 RELElisten-Extraktor",
        icon=":material/table_view:",
    )
with right:
    st.page_link(
        "app_pages/tool_1052_buchungsimporteur.py",
        label="1052 Buchungsimporteur",
        icon=":material/receipt_long:",
    )

st.info(
    "Hinweis: Dieses Repo enthaelt die Orchestrierung. "
    "Die Fachlogik bleibt in den einzelnen Tool-Repositories."
)
