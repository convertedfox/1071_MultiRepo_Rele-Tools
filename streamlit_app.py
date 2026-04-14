from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dashboard.state import init_state  # noqa: E402

st.set_page_config(
    page_title="RELE Tool Dashboard",
    page_icon=":material/dashboard:",
    layout="wide",
)

init_state(st.session_state)

page = st.navigation(
    [
        st.Page("app_pages/home.py", title="Start", icon=":material/home:"),
        st.Page(
            "app_pages/tool_1049_pdf_extraktor.py",
            title="1049 PDF-Extraktor",
            icon=":material/picture_as_pdf:",
        ),
        st.Page(
            "app_pages/tool_1067_relelisten_extraktor.py",
            title="1067 RELElisten-Extraktor",
            icon=":material/table_view:",
        ),
        st.Page(
            "app_pages/tool_1052_buchungsimporteur.py",
            title="1052 Buchungsimporteur",
            icon=":material/receipt_long:",
        ),
    ],
    position="top",
)

st.title(f"{page.icon} {page.title}")
st.caption("Ein Einstiegspunkt fuer die LBV-Toolkette (1049 -> 1067 optional -> 1052).")

page.run()
