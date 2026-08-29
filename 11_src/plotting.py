"""Plotting style — consistent, professional, notebook-friendly.

Import and call `apply_style()` once at the top of each notebook.
Colour palette is colourblind-friendly and muted (research, not decoration).
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns

# Colourblind-friendly palette (Okabe-Ito inspired, muted for research)
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#F0E442", "#56B4E9", "#E69F00", "#999999"]
SEQUENTIAL = "Blues"  # for heatmaps


def apply_style() -> None:
    sns.set_theme(style="whitegrid", context="notebook", palette=PALETTE)
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "figure.figsize": (10, 5),
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "font.family": "sans-serif",
        }
    )


# Model ladder colours (stable across all notebooks)
MODEL_COLOURS = {
    "Naive": "#999999",
    "Seasonal Naive": "#666666",
    "Moving Average": "#0072B2",
    "SES": "#009E73",
    "DES": "#D55E00",
    "TES": "#CC79A7",
    "ARIMA": "#E69F00",
    "SARIMA": "#56B4E9",
    "LSTM": "#F0E442",
    "LLM": "#D55E00",
}
