"""Central configuration — single source of truth for seeds, paths, and defaults.

All notebooks import from here so that seeds, paths, and display settings
stay consistent. Nothing here locks experimental parameters (horizon, sample
size, costs, etc.) — those are decided in the notebooks and recorded in
decisions.md. This file only holds reproducibility scaffolding.
"""
from __future__ import annotations

import os
import random
import pathlib

import numpy as np

# ---------------------------------------------------------------------------
# Project root (one level above 11_src/)
# ---------------------------------------------------------------------------
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]

# Canonical subdirectories (created by the reset)
DATA_RAW_M5 = PROJECT_ROOT / "02_data" / "dataset_01_m5" / "raw"
DATA_RAW_SIT = PROJECT_ROOT / "02_data" / "dataset_02_store_item_demand" / "raw"
PROCESSED = PROJECT_ROOT / "03_processed_data"
MODELS_DIR = PROJECT_ROOT / "04_models"
EXPERIMENTS_DIR = PROJECT_ROOT / "05_experiments"
RESULTS_DIR = PROJECT_ROOT / "06_results"
FIGURES_DIR = PROJECT_ROOT / "07_figures"
NOTEBOOKS_DIR = PROJECT_ROOT / "08_notebooks"
REPORTS_DIR = PROJECT_ROOT / "09_reports"
REFERENCES_DIR = PROJECT_ROOT / "10_references"

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
GLOBAL_SEED = 42


def seed_everything(seed: int = GLOBAL_SEED) -> None:
    """Set seeds for Python, NumPy, and hash randomization."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    # torch seeding is added in the LSTM notebook if torch is available


def ensure_dirs() -> None:
    for p in [PROCESSED, MODELS_DIR, EXPERIMENTS_DIR, RESULTS_DIR, FIGURES_DIR, REPORTS_DIR, REFERENCES_DIR]:
        p.mkdir(parents=True, exist_ok=True)
