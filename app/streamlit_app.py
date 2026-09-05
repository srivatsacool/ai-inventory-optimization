"""AI Inventory Optimization - Interactive Research Laboratory (shell).

<!-- DESIGN CONTRACT — implements AI_Inventory_Optimization_DESIGN.md (binding).
THESIS: the Lab is a flagship analytical instrument, not an embedded widget:
question -> control -> visualization -> interpretation, everywhere.
OWN-WORLD: lab-bg #080C16 navy, four surface levels, hairlines, steel/teal/
indigo/violet accents, frozen-amber vs interactive-blue status system,
Inter + JetBrains Mono. No stock Streamlit chrome.
STORY: visitor enters from HOME's thesis and immediately scans the frozen
truth (4 number cards + charts), then interrogates models and policies.
FORM: DESIGN.md sections 3,4,5,6,7,8,9,19. FINISH: unreviewed and
undocumented is unfinished; this build ends with the finish review, the
verdict, and DESIGN.md. -->

Entry point. Run from repo root:
    streamlit run app/streamlit_app.py

Research integrity: frozen evidence (tag v1.0-evidence-freeze) is read-only
via app.lib.frozen_loader; interactive/derived data via app.lib.appdata_loader
(app_data/), always labeled. This file never computes research values.
"""

import streamlit as st
from pathlib import Path

from app.lib.lab import inject_theme

HERE = Path(__file__).resolve().parent
PAGES = HERE / "views"  # "views", not "pages": st.navigation owns the nav;
                        # a pages/ directory would auto-inject a second nav.

st.set_page_config(
    page_title="Research Lab · AI Inventory Optimization",
    page_icon=":material/science:",
    layout="wide",
    initial_sidebar_state="auto",
)

inject_theme()

NAV = [
    ("01", "Frozen Results", "01_Frozen_Results.py"),
    ("02", "Forecast Explorer", "02_Forecast_Explorer.py"),
    ("03", "Inventory Lab", "03_Inventory_Sensitivity.py"),
    ("04", "Methodology", "04_Methodology.py"),
]


def main():
    st.sidebar.markdown(
        """<div style="padding:4px 4px 10px;">
        <div style="font-size:15px;font-weight:700;letter-spacing:-.01em;color:#F7F8FA;">AI Inventory Optimization</div>
        <div style="font-size:11px;font-weight:650;letter-spacing:.14em;text-transform:uppercase;color:#8B94A5;margin-top:3px;">Interactive Research Laboratory</div>
        </div>""",
        unsafe_allow_html=True,
    )
    pages = [st.Page(str(PAGES / f), title=f"{num} · {name}") for num, name, f in NAV]
    nav = st.navigation({"Research Lab": pages}, position="sidebar")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """<div style="font-size:11px;color:#626B7A;line-height:1.7;">
        <span style="color:#D8B376;">◆</span> Locked / published evidence<br>
        <span style="color:#7FBDE6;">◆</span> Interactive / experimental<br><br>
        Evidence freeze: v1.0-evidence-freeze.<br>Interactive pages never alter frozen numbers.
        </div>""",
        unsafe_allow_html=True,
    )
    nav.run()


if __name__ == "__main__":
    main()
