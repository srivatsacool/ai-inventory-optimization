"""Diagnostic figures + Demand DNA for the Interactive Experiment sandbox.

All builders are pure: they take dataframes/arrays and return Plotly figures or
plain dicts. Rendering uses the shared lab component kit.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .lab import FONT_MONO, FONT_UI, INK, INK_MUTE, LINE, TRAD, fig_base, model_color

SEASON = 7


# ---------------------------------------------------------------------------
# Demand DNA
# ---------------------------------------------------------------------------


def demand_dna(demand: np.ndarray) -> dict:
    d = np.asarray(demand, dtype=float)
    n = len(d)
    zero_rate = float((d == 0).mean())
    pos = d[d > 0]
    adi = float(n / len(pos)) if len(pos) else float("inf")  # average demand interval
    cv2 = float((pos.std() / pos.mean()) ** 2) if len(pos) and pos.mean() > 0 else 0.0
    cv = float(d.std() / d.mean()) if d.mean() > 0 else 0.0
    x = np.arange(n)
    trend = float(np.polyfit(x, d, 1)[0]) if n > 2 else 0.0
    week_idx = np.arange(n) % 7
    weekly_strength = 0.0
    if d.std() > 0:
        week_means = np.array([d[week_idx == w].mean() for w in range(7)])
        weekly_strength = float(max(0.0, 1 - (d - week_means[week_idx]).var() / d.var()))
    arch = "smooth" if (adi < 1.32 and cv2 < 0.49) else \
           "intermittent" if (adi >= 1.32 and cv2 < 0.49) else \
           "erratic" if (adi < 1.32) else "lumpy"
    return {"zero_rate": zero_rate, "ADI": adi, "CV2": cv2, "CV": cv, "mean": float(d.mean()),
            "trend_per_day": trend, "weekly_seasonality": weekly_strength, "syntos_type": arch, "n": n}


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------


def fig_forecast_overlay(dates_hist, hist, dates_eval, actual, fc_by_model: dict,
                         shaded: str = ""):
    import plotly.graph_objects as go

    fig = fig_base(height=430)
    fig.add_trace(go.Scatter(x=dates_hist, y=hist, name="History", mode="lines",
                             line=dict(color="#9A9DA4", width=1.4)))
    fig.add_trace(go.Scatter(x=dates_eval, y=actual, name="Actual", mode="lines+markers",
                             line=dict(color=INK, width=2.6), marker=dict(size=6)))
    for name, fc in fc_by_model.items():
        fig.add_trace(go.Scatter(x=dates_eval, y=fc, name=name, mode="lines",
                                 line=dict(color=model_color(name), width=1.7, dash="dot" if shaded == name else None)))
    fig.add_vrect(x0=dates_eval.iloc[0], x1=dates_eval.iloc[-1], fillcolor="rgba(53,97,138,.05)",
                  line_width=0, annotation_text="evaluation window",
                  annotation_font=dict(size=10, color=INK_MUTE))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.22, font=dict(size=11)))
    fig.update_yaxes(title="Demand (units)")
    return fig


def fig_error_distribution(fc_by_model: dict, actual, models: list[str]):
    import plotly.graph_objects as go

    fig = fig_base(height=380)
    for name in models:
        fc = fc_by_model.get(name)
        if fc is None:
            continue
        err = np.asarray(fc, dtype=float) - np.asarray(actual, dtype=float)
        fig.add_trace(go.Box(y=err, name=name, marker_color=model_color(name),
                             boxpoints=False, line=dict(width=1.4)))
    fig.update_layout(showlegend=False)
    fig.update_yaxes(title="Forecast error (forecast − actual)")
    return fig


def fig_accuracy_vs_cost(metrics_df: pd.DataFrame, inventory_df: pd.DataFrame,
                         metric: str = "MAE"):
    import plotly.graph_objects as go

    df = metrics_df.merge(inventory_df[["model", "total_cost", "service_level"]], on="model", how="inner")
    if not len(df):
        return fig_base(height=420)
    fig = fig_base(height=420)
    best_mae = df.loc[df[metric].idxmin()]
    best_cost = df.loc[df["total_cost"].idxmin()]
    for _, r in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[r[metric]], y=[r["total_cost"]], mode="markers+text", name=r["model"],
            text=[r["model"]], textposition="top center",
            textfont=dict(size=10, family=FONT_MONO),
            marker=dict(size=13, color=model_color(r["model"]), line=dict(width=1, color="#FAF8F4")),
            hovertemplate=f"<b>{r['model']}</b><br>{metric}: %{{x:.3f}}<br>total cost: %{{y:.1f}}<extra></extra>",
        ))
    fig.update_layout(showlegend=False,
                      annotations=[
                          dict(x=best_mae[metric], y=best_mae["total_cost"],
                               text=f"best {metric}", ax=20, ay=-30, showarrow=True,
                               font=dict(size=10, family=FONT_MONO, color=TRAD)),
                          dict(x=best_cost[metric], y=best_cost["total_cost"],
                               text="lowest cost", ax=20, ay=-30, showarrow=True,
                               font=dict(size=10, family=FONT_MONO, color="#2A9D8F"))])
    fig.update_xaxes(title=f"{metric} (lower = better forecaster)")
    fig.update_yaxes(title="Total inventory cost (lower = better)")
    return fig


def fig_cost_decomposition(inventory_df: pd.DataFrame):
    import plotly.graph_objects as go

    df = inventory_df.sort_values("total_cost")
    fig = fig_base(height=400)
    fig.add_trace(go.Bar(x=df["model"], y=df["total_holding_cost"], name="Holding cost",
                         marker_color="#2A9D8F"))
    fig.add_trace(go.Bar(x=df["model"], y=df["total_stockout_cost"], name="Stockout cost",
                         marker_color="#C25B64"))
    fig.update_layout(barmode="stack", legend=dict(orientation="h", y=1.06))
    fig.update_yaxes(title="Cost (H=1 per unit-day, P per unit short)")
    return fig


def fig_service_cost_frontier(inventory_df: pd.DataFrame):
    import plotly.graph_objects as go

    df = inventory_df.copy()
    fig = fig_base(height=420)
    fig.add_trace(go.Scatter(x=df["service_level"], y=df["total_cost"], mode="markers+text",
                             text=df["model"], textposition="top center",
                             textfont=dict(size=10, family=FONT_MONO),
                             marker=dict(size=13, color=[model_color(m) for m in df["model"]],
                                         line=dict(width=1, color="#FAF8F4")),
                             name="model"))
    # Pareto frontier (min cost at each service level)
    df2 = df.sort_values("service_level")
    front_y = np.minimum.accumulate(df2["total_cost"].values[::-1])[::-1]
    fig.add_trace(go.Scatter(x=df2["service_level"], y=front_y, mode="lines",
                             line=dict(color=LINE, width=1.5, dash="dot"),
                             showlegend=False, hoverinfo="skip"))
    fig.update_xaxes(title="Service level (fill rate)", tickformat=".1%")
    fig.update_yaxes(title="Total inventory cost")
    return fig


def fig_heatmap(pivot: pd.DataFrame, title: str, colorscale: str = "RdYlGn",
                reverse: bool = False, fmt: str = ".2f"):
    import plotly.graph_objects as go

    z = pivot.values.astype(float)
    zshow = -z if reverse else z
    fig = go.Figure(go.Heatmap(
        z=zshow, x=[str(c) for c in pivot.columns], y=pivot.index,
        colorscale=colorscale, zsmooth=False,
        customdata=z, hovertemplate="%{y} × %{x}: %{customdata:" + fmt + "} <extra></extra>",
        colorbar=dict(tickfont=dict(size=10)),
        text=[[fmt.format(v) for v in row] for row in z], texttemplate="%{text}",
        textfont=dict(size=10, family=FONT_MONO),
    ))
    fig.update_layout(height=max(300, 34 * len(pivot) + 110), title=title,
                      title_font=dict(size=14, family=FONT_UI, color=INK),
                      margin=dict(l=10, r=10, t=52, b=10))
    fig.update_xaxes(tickfont=dict(size=10.5, family=FONT_MONO))
    fig.update_yaxes(tickfont=dict(size=10.5, family=FONT_MONO))
    return fig


def fig_series_profile(dates, demand):
    import plotly.graph_objects as go

    fig = fig_base(height=280)
    fig.add_trace(go.Scatter(x=dates, y=demand, mode="lines",
                             line=dict(color=TRAD, width=1.4)))
    fig.update_yaxes(title="Demand")
    return fig


def accuracy_value_gap(metrics_df: pd.DataFrame, inventory_df: pd.DataFrame,
                       metric: str = "MAE") -> dict:
    """The Accuracy ≠ Value computation. Pure data — nothing hard-coded."""
    df = metrics_df.merge(inventory_df[["model", "total_cost", "service_level", "average_inventory"]],
                          on="model", how="inner")
    if not len(df):
        return {}
    best_acc = df.loc[df[metric].idxmin()]
    best_val = df.loc[df["total_cost"].idxmin()]
    return {
        "best_forecaster": best_acc["model"],
        "best_forecaster_cost": float(best_acc["total_cost"]),
        "best_cost_model": best_val["model"],
        "best_cost": float(best_val["total_cost"]),
        "gap_abs": float(best_acc["total_cost"] - best_val["total_cost"]),
        "gap_pct": float((best_acc["total_cost"] / max(best_val["total_cost"], 1e-9) - 1) * 100),
        "agrees": bool(best_acc["model"] == best_val["model"]),
    }
