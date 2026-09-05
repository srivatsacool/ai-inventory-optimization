"""Page 2 - Forecast Explorer. INTERACTIVE / DERIVED, not evidence.

Placeholder scaffold: shows representative series actuals plus a small cached
forecast sample from app_data/. Per-series live fitting (Naive/MA/SES/...)
arrives in a later phase; no model training in this scaffold.
"""

import streamlit as st

from app.lib import appdata_loader as A

st.title("Forecast Explorer")
st.caption("INTERACTIVE LAB - derived sample data. Not part of the frozen published evidence.")

status = A.check_all_present()
missing = [k for k, ok in status.items() if not ok]
if missing:
    st.warning(f"app_data missing: {missing}. Run: python scripts/build_app_data.py")
    st.stop()

rep = A.load_representative_series()
fc = A.load_forecasts_sample()

series = st.selectbox("Series", sorted(rep["series_id"].unique().tolist()))
srep = rep[rep["series_id"] == series].sort_values("forecast_date")
st.subheader(f"Actuals - {series} (origin 1, H28 sample)")
st.line_chart(srep.set_index("forecast_date")["actual"])

models = sorted(fc["model"].unique().tolist()) if not fc.empty else []
chosen = st.multiselect("Cached forecast models", models, default=models[:3] if models else [])
if chosen and not fc.empty:
    sub = fc[(fc["series_id"] == series) & (fc["model"].isin(chosen))]
    st.subheader("Cached forecasts vs actuals")
    st.dataframe(sub, use_container_width=True)
else:
    st.info("Select a cached model to inspect its sample forecasts. Live per-series fitting is out of scope for this scaffold.")
