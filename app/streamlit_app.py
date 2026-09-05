"""AI Inventory Optimization - Interactive Laboratory (Streamlit shell, v0.1 scaffold).

Entry point. Run from repo root:
    streamlit run app/streamlit_app.py

Branch: app/streamlit-v1. Frozen evidence (tag v1.0-evidence-freeze) is
read-only: pages under FROZEN EVIDENCE read only tracked files from the
frozen head via app.lib.frozen_loader. Everything interactive/derived lives
in app_data/ and is labeled as such in the UI.
"""

import streamlit as st

st.set_page_config(
    page_title="AI Inventory Optimization - Interactive Lab",
    layout="wide",
)

HOME = """
# AI Inventory Optimization - Interactive Laboratory

## Read the research. Run the research. Interpret the decision.

Locked thesis: **LSTM wins forecast accuracy on both datasets, but forecast
accuracy does not guarantee inventory-cost optimality - Moving Average wins
Store inventory cost.**

### Two modes

- FROZEN EVIDENCE - the published result. Exactly as frozen at
  tag v1.0-evidence-freeze. No parameter changes, no recomputation.
- INTERACTIVE LAB - your own scenario. Clearly labeled, never mixed with
  frozen numbers.
"""


def main():
    pages = [
        st.Page("app/pages/01_Frozen_Results.py", title="Frozen Results", icon=":material/lock:"),
        st.Page("app/pages/02_Forecast_Explorer.py", title="Forecast Explorer", icon=":material/show_chart:"),
        st.Page("app/pages/03_Inventory_Sensitivity.py", title="Inventory / Sensitivity", icon=":material/inventory_2:"),
        st.Page("app/pages/04_Methodology.py", title="Methodology", icon=":material/description:"),
    ]
    nav = st.navigation({"Explore": pages}, position="sidebar")
    st.sidebar.markdown("---")
    st.sidebar.caption("Scaffold v0.1 on branch app/streamlit-v1. Frozen tag: v1.0-evidence-freeze.")
    nav.run()


if __name__ == "__main__":
    main()
