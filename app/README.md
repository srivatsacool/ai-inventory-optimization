# Interactive Laboratory (scaffold v0.1, branch app/streamlit-v1)

Run from repo root:

  streamlit run app/streamlit_app.py

Boundaries:

- FROZEN EVIDENCE (tag v1.0-evidence-freeze) is read-only. Page 01 reads only
  tracked files via app/lib/frozen_loader.py. Never add recomputation there.
- INTERACTIVE LAB data lives in app_data/ (derived, small, tracked). Pages
  02-03 read it via app/lib/appdata_loader.py and label it as derived.
- No model training in this phase. Forecast Explorer shows cached samples;
  live per-series fitting is a later phase.

Regenerate derived data:

  python scripts/build_app_data.py
