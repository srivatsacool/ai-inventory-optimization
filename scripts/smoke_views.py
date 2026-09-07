"""Smoke-test every app view with streamlit.testing.v1.AppTest.

Run from repo root:  python scripts/smoke_views.py
Exit 1 if any page raises.
"""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))  # `from lib import ...` like the live app

from streamlit.testing.v1 import AppTest  # noqa: E402

failures = 0


def run_page(fname: str, seed_exp=None):
    global failures
    at = AppTest.from_file(str(ROOT / "app" / "views" / fname), default_timeout=600)
    if seed_exp is not None:
        at.session_state["exp"] = seed_exp
    at.run()
    n_exc = len(at.exception)
    status = "PASS" if n_exc == 0 else "FAIL"
    failures += n_exc
    print(f"{status}  {fname}  (exceptions: {n_exc})")
    for ex in at.exception:
        print("   ", str(ex.message)[:500].replace("\n", " | "))
        print("   ", str(ex.stack_trace)[-400:].replace("\n", " | ") if ex.stack_trace else "")
    return at


print("=== static pages ===")
for f in ["01_Overview.py", "02_Research_Benchmark.py", "11_Methodology.py"]:
    run_page(f)

print("\n=== building a sandbox experiment (bare mode) ===")
from lib import engine as E  # noqa: E402
from lib import state  # noqa: E402

series = E.get_series("m5", "FOODS_1_098_CA_3_evaluation")
e = state.build_experiment(
    "Built-in", "m5", "m5", "FOODS_1_098_CA_3_evaluation", series, 28,
    {}, ["Naive", "Seasonal Naive", "Moving Average", "SES", "DES", "TES", "ARIMA",
         "Croston", "SBA", "TSB"],
    dict(E.POLICY_DEFAULT),
)
print("experiment built:", e["exp_id"], "| models:", len(e["models"]),
      "| metrics rows:", len(e["metrics_df"]), "| inventory rows:", len(e["inventory_df"]))
at_session = {"exp": e, "run_log": []}

print("\n=== sandbox pages (with experiment seeded) ===")
for f in ["04_Forecast_Lab.py", "05_Model_Arena.py", "06_Inventory_Simulator.py",
          "07_Policy_Lab.py", "08_Decision_Center.py", "09_Diagnostics.py",
          "10_Experiments.py"]:
    at = AppTest.from_file(str(ROOT / "app" / "views" / f), default_timeout=600)
    at.session_state["exp"] = e
    at.session_state["run_log"] = []
    at.run()
    n_exc = len(at.exception)
    status = "PASS" if n_exc == 0 else "FAIL"
    failures += n_exc
    print(f"{status}  {f}  (exceptions: {n_exc})")
    for ex in at.exception:
        print("   ", str(ex.message)[:500].replace("\n", " | "))

print("\n=== Data Studio (builds its own experiment in-runtime) ===")
at = AppTest.from_file(str(ROOT / "app" / "views" / "03_Data_Studio.py"), default_timeout=600)
at.run()
n_exc = len(at.exception)
print(("PASS" if n_exc == 0 else "FAIL"), " 03_Data_Studio.py  (exceptions:", n_exc, ")")
for ex in at.exception:
    print("   ", str(ex.message)[:500].replace("\n", " | "))

print("\nRESULT:", "ALL PASS" if failures == 0 and n_exc == 0 else f"{failures + n_exc} FAILURES")
sys.exit(1 if (failures or n_exc) else 0)
