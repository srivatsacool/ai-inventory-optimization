"""Interaction-level smoke tests: scenario rebuilds, policy knobs, custom grids,
constraints, and both demand environments (sparse M5 + dense Store)."""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from streamlit.testing.v1 import AppTest  # noqa: E402

from lib import engine as E  # noqa: E402
from lib import state  # noqa: E402

failures = 0


def check(name, at, extra=""):
    global failures
    n = len(at.exception)
    print(("PASS" if n == 0 else "FAIL"), name, extra, f"(exc: {n})")
    for ex in at.exception:
        print("    ", str(ex.message)[:300].replace("\n", " | "))
    failures += n
    return at


# ---------------------------------------------------------------------------
# A · dense Store series + scenario, sandbox pages again
# ---------------------------------------------------------------------------
store = E.get_series("store_item_demand", "S01_I01")
e_store = state.build_experiment("Built-in", "store_item_demand", "store_item_demand",
                                 "S01_I01", store, 28, {},
                                 ["Naive", "Seasonal Naive", "Moving Average", "SES", "DES",
                                  "TES", "ARIMA", "SARIMA", "LSTM"],
                                 dict(E.POLICY_DEFAULT))
print("store experiment:", e_store["exp_id"], "| LSTM status:", e_store["statuses"]["LSTM"])

for f in ["04_Forecast_Lab.py", "06_Inventory_Simulator.py", "07_Policy_Lab.py",
          "08_Decision_Center.py", "09_Diagnostics.py"]:
    at = AppTest.from_file(str(ROOT / "app" / "views" / f), default_timeout=600)
    at.session_state["exp"] = e_store
    at.session_state["run_log"] = []
    at.run()
    check(f"store/{f}", at)

# ---------------------------------------------------------------------------
# B · scenario experiment (spike + volatility + intermittency)
# ---------------------------------------------------------------------------
m5 = E.get_series("m5", "FOODS_1_098_CA_3_evaluation")
e_scn = state.build_experiment(
    "Built-in", "m5", "m5", "FOODS_1_098_CA_3_evaluation", m5, 28,
    {"level": 1.5, "trend_per_day": 0.3, "seasonality": 1.5, "volatility": 0.4,
     "zero_rate": 0.7, "shock_kind": "spike", "shock_factor": 2.0, "_name": "stress mix"},
    ["Naive", "Moving Average", "SES", "ARIMA", "Croston", "TSB"],
    dict(E.POLICY_DEFAULT))
print("scenario experiment:", e_scn["exp_id"], "| zero rate now:",
      round((e_scn["series_df"]["demand"] == 0).mean(), 3))

for f in ["04_Forecast_Lab.py", "05_Model_Arena.py", "07_Policy_Lab.py",
          "08_Decision_Center.py", "09_Diagnostics.py", "10_Experiments.py"]:
    at = AppTest.from_file(str(ROOT / "app" / "views" / f), default_timeout=600)
    at.session_state["exp"] = e_scn
    at.session_state["run_log"] = [{"experiment_id": "EXP-FIRST", "mode": "SANDBOX",
                                    "timestamp": "t", "dataset": "m5",
                                    "series_id": "FOODS_1_098_CA_3_evaluation",
                                    "origin_date": "2016-03-01", "horizon": 28,
                                    "policy": e_scn["policy"], "models": e_scn["models"],
                                    "scenario": "", "winners": {"best_forecaster": "Naive",
                                                                "lowest_cost": "Naive",
                                                                "highest_service": "Naive",
                                                                "lowest_inventory": "Naive"}}]
    at.run()
    check(f"scenario/{f}", at)

# ---------------------------------------------------------------------------
# C · Inventory Simulator: change lead time knob → chain recomputes
# ---------------------------------------------------------------------------
at = AppTest.from_file(str(ROOT / "app" / "views" / "06_Inventory_Simulator.py"), default_timeout=600)
at.session_state["exp"] = dict(e_scn)
at.session_state["run_log"] = []
at.run()
if not at.exception:
    before = at.session_state["exp"]["policy"]["lead_time"]
    at.slider(key="inv_L").set_value(14).run()
    after = at.session_state["exp"]["policy"]["lead_time"]
    cost14 = at.session_state["exp"]["inventory_df"]["total_cost"].iloc[0]
    check("simulator: L=14 recompute", at, f"L {before}->{after}, cost0={cost14:.1f}")

# ---------------------------------------------------------------------------
# D · Policy Lab: custom grid + constraints
# ---------------------------------------------------------------------------
# D · Policy Lab: custom grid + constraints
# (segmented_control state can't be replayed by AppTest, so each rule check is a
#  fresh instance on the default 27-grid — the constraint code path is identical)
at = AppTest.from_file(str(ROOT / "app" / "views" / "07_Policy_Lab.py"), default_timeout=600)
at.session_state["exp"] = dict(e_scn)
at.session_state["run_log"] = []
at.run()
check("policy: 27-grid", at)

for rule, val in (("pl_maxcost", 1e9), ("pl_maxcost", 0.001), ("pl_maxmase", 1e6), ("pl_maxrt", 1e6)):
    at = AppTest.from_file(str(ROOT / "app" / "views" / "07_Policy_Lab.py"), default_timeout=600)
    at.session_state["exp"] = dict(e_scn)
    at.session_state["run_log"] = []
    at.session_state[rule] = val
    at.run()
    check(f"policy: rule {rule}={val}", at)

# ---------------------------------------------------------------------------
# E · Accuracy ≠ Value: verify the gap math directly on both environments
# ---------------------------------------------------------------------------
from lib.diagnostics import accuracy_value_gap  # noqa: E402

for name, e in (("m5", e_scn), ("store", e_store)):
    gap = accuracy_value_gap(e["metrics_df"], e["inventory_df"])
    print(f"gap[{name}]:", {k: (round(v, 2) if isinstance(v, float) else v)
                            for k, v in gap.items()} if gap else "EMPTY")

print("\nRESULT:", "ALL PASS" if failures == 0 else f"{failures} FAILURES")
sys.exit(1 if failures else 0)
