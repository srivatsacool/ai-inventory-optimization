"""Page 4 - Methodology. Frozen protocol summary, tracked sources only."""

import streamlit as st

from app.lib import frozen_loader as F

st.title("Methodology")
st.caption("Frozen experimental protocol. Sources tracked at v1.0-evidence-freeze.")

st.markdown("""
- 500 M5 series (sparse / intermittent) + 500 Store-Item-Demand series (dense).
- 8 rolling origins, 28-day horizon, frozen temporal split, seed 42.
- Train 2013-01-01 to 2015-10-31 (1034 d); validation 2015-11-01 to 2016-02-29
  (121 d, includes leap day); test 2016-03-01 to 2016-05-22 (83 d).
- 12 approaches: Naive, Seasonal Naive, Moving Average, SES, DES, TES, ARIMA,
  SARIMA (Store only, full-500), Croston / SBA / TSB (M5 only), LSTM.
- Shared daily-review order-up-to policy with lost sales; default L7 / 95% /
  H=1 / P=5; 27-policy sensitivity grid L{3,7,14} x svc{.90,.95,.99} x P{3,5,10}.
- 112,000 forecasts per model-dataset; 91 paired comparisons; validation gates.
""")

p = F.frozen_path("protocol_doc")
if p.exists():
    st.subheader("Experiment protocol (tracked doc)")
    st.code(p.read_text(encoding="utf-8")[:4000])
else:
    st.warning(f"Protocol doc missing: {p}")

st.subheader("Decision log pointer")
st.write("Significant decisions are recorded in 00_project/decisions.md (tracked), including the leap-day correction, SARIMA full-500 choice, and leakage-safe protocol.")
