"""AI Inventory Optimization - Interactive Research Laboratory (shell).

<!-- DESIGN CONTRACT — implements MASTER.md (2026-09-06 paint pass, binding).
THESIS: warm cream editorial laboratory — paper #FAF8F4, panel #F3EFE6, ink
#1E222A, steel-blue structure #35618A, 12-hue MODEL_COLORS data palette as
the color heroes. frozen-amber vs interactive-blue status system. Inter +
JetBrains Mono. No stock Streamlit chrome, no dark mode.
STORY: visitor enters from HOME's thesis and immediately scans the frozen
truth (4 number cards + charts), then interrogates models and policies.
FORM: MASTER.md sections 1,2,3,6,9. FINISH: unreviewed and undocumented is
unfinished; this build ends with the finish review and MASTER.md. -->

Entry point. Run from repo root:
    streamlit run app/streamlit_app.py

Research integrity: frozen evidence (tag v1.0-evidence-freeze) is read-only
via app.lib.frozen_loader; interactive/derived data via app.lib.appdata_loader
(app_data/), always labeled. This file never computes research values.
"""

import streamlit as st
from pathlib import Path

# NOTE: Streamlit always puts the entrypoint's own directory (app/) on
# sys.path — locally and on Community Cloud — so `lib` (app/lib/, a proper
# subpackage) imports with no path hacks and no dependence on the CWD.
from lib.lab import inject_theme

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
    ("01", "Overview", "01_Overview.py"),
    ("02", "Research Benchmark", "02_Research_Benchmark.py"),
    ("03", "Data Studio", "03_Data_Studio.py"),
    ("04", "Forecast Lab", "04_Forecast_Lab.py"),
    ("05", "Model Arena", "05_Model_Arena.py"),
    ("06", "Inventory Simulator", "06_Inventory_Simulator.py"),
    ("07", "Policy Lab", "07_Policy_Lab.py"),
    ("08", "Decision Center", "08_Decision_Center.py"),
    ("09", "Diagnostics", "09_Diagnostics.py"),
    ("10", "Experiments", "10_Experiments.py"),
    ("11", "Research / Methodology", "11_Methodology.py"),
]


def main():
    st.sidebar.markdown(
        """<div style="padding:4px 4px 10px;">
        <div style="font-size:15px;font-weight:700;letter-spacing:-.01em;color:#1E222A;">AI Inventory Optimization Lab</div>
        <div style="font-size:11px;font-weight:650;letter-spacing:.14em;text-transform:uppercase;color:#8A8D93;margin-top:3px;">From Forecasts to Shelf Decisions</div>
        </div>""",
        unsafe_allow_html=True,
    )
    frozen = [("02", "Research Benchmark", "02_Research_Benchmark.py"),
              ("11", "Research / Methodology", "11_Methodology.py")]
    sandbox = [(n, t, f) for n, t, f in NAV if (n, t, f) not in frozen]
    nav = st.navigation({
        "Lab": [st.Page(str(PAGES / f), title=f"{n} · {t}") for n, t, f in sandbox],
        "Research": [st.Page(str(PAGES / f), title=f"{n} · {t}") for n, t, f in frozen],
    }, position="sidebar")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """<div style="font-size:11px;color:#6A6E76;line-height:1.7;">
        <span style="color:#B08D3F;">◆</span> Locked / published evidence<br>
        <span style="color:#2C6E9E;">◆</span> Interactive / experimental<br><br>
        Evidence freeze: v1.0-evidence-freeze.<br>Interactive pages never alter frozen numbers.
        </div>""",
        unsafe_allow_html=True,
    )
    nav.run()


if __name__ == "__main__":
    main()
