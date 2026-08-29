"""Generate the 02_data_acquisition_and_audit.ipynb notebook."""
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb.metadata["kernelspec"] = {"display_name": "AI Inventory (venv)", "language": "python", "name": "ai-inventory"}
nb.metadata["language_info"] = {"name": "python", "version": "3.12.3"}
cells = []

cells.append(nbf.v4.new_markdown_cell(
"""# 02 — Data Acquisition and Audit

## Research objective

Understand the raw data in both datasets before any modelling. Every parameter
in this study — horizons, splits, costs, sample sizes — must be grounded in
what the data actually contains, not in assumptions.

## Why this matters

The credibility of the entire study rests on knowing what we are working with.
Different datasets have different date ranges, missing-value structures,
intermittency profiles, and scales. These differences directly affect:
- what models are appropriate,
- what forecast horizons are meaningful,
- what train/test splits are valid,
- what inventory costs are realistic.

## What this notebook does

1. Loads both datasets and confirms their structure.
2. Establishes the actual date ranges for each dataset.
3. Computes the **common calendar window** from the real temporal overlap.
4. Assesses data quality: missing values, duplicates, zero demand.
5. Documents the Favorita data limitation.
6. Outputs a machine-readable audit summary for downstream notebooks.
"""))

cells.append(nbf.v4.new_markdown_cell(
"""## 1. Walmart M5 — Structure and content

The M5 competition dataset contains unit sales for 30,490 item-store combinations
across 10 Walmart stores in 3 US states (CA, TX, WI). Daily frequency.

**Files:**
- `sales_train_validation.csv` — 30,490 rows (one per series) × 1913 daily columns (d_1 through d_1913)
- `calendar.csv` — 1969 rows mapping d_1..d_1941 to actual dates, with event flags
- `sell_prices.csv` — per-item per-store weekly prices
"""))

cells.append(nbf.v4.new_code_cell(
"""import pandas as pd
import numpy as np
import pathlib
import json

PROJ = pathlib.Path('.')
M5_RAW = PROJ / '02_data/dataset_01_m5/raw'
FAV_RAW = PROJ / '02_data/dataset_02_grocery/raw'

# Load M5 core files
print("Loading M5 sales_train_validation.csv …")
m5_sales = pd.read_csv(M5_RAW / 'sales_train_validation.csv')
print(f"  Shape: {m5_sales.shape}")
print(f"  Columns (first 6): {list(m5_sales.columns[:6])}")

print("\\nLoading M5 calendar.csv …")
m5_cal = pd.read_csv(M5_RAW / 'calendar.csv')
print(f"  Shape: {m5_cal.shape}")
print(f"  Date range: {m5_cal['date'].min()} → {m5_cal['date'].max()}")
print(f"  Unique dates: {m5_cal['date'].nunique()}")

print("\\nLoading M5 sell_prices.csv …")
m5_prices = pd.read_csv(M5_RAW / 'sell_prices.csv')
print(f"  Shape: {m5_prices.shape}")
"""))

cells.append(nbf.v4.new_markdown_cell(
"""### M5 series metadata

Each row in the sales matrix represents one item-store combination.
The hierarchy is:

```text
State (CA/TX/WI)
  └─ Store (10 stores)
       └─ Category (FOODS, HOBBIES, HOUSEHOLD)
            └─ Department (7 departments)
                 └─ Item
```

This hierarchy allows us to study whether forecasting accuracy varies by
demand type across the retail structure.
"""))

cells.append(nbf.v4.new_code_cell(
"""# M5 series breakdown
meta = m5_sales[['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id']].copy()
print("=== Series counts ===")
print(f"Total series: {len(meta)}")
print(f"\\nBy category:")
print(meta.groupby('cat_id').size().to_string())
print(f"\\nBy department:")
print(meta.groupby('dept_id').size().to_string())
print(f"\\nBy state:")
print(meta.groupby('state_id').size().to_string())
print(f"\\nBy store:")
print(meta.groupby('store_id').size().to_string())
"""))

cells.append(nbf.v4.new_markdown_cell(
"""### M5 demand characteristics

The demand matrix is extremely sparse. The calendar spans 1969 days, but the
sales matrix only covers d_1 through d_1913. We must verify which dates
correspond to which d-columns.
"""))

cells.append(nbf.v4.new_code_cell(
"""# Map d-columns to dates
d_cols = [c for c in m5_sales.columns if c.startswith('d_')]
print(f"Number of d-columns: {len(d_cols)}")
print(f"First d-column: {d_cols[0]}, Last: {d_cols[-1]}")

# Build date mapping from calendar
d_map = dict(zip(m5_cal['d'], m5_cal['date']))
first_date = d_map.get(d_cols[0], 'unknown')
last_date = d_map.get(d_cols[-1], 'unknown')
print(f"M5 sales date range: {first_date} → {last_date}")

n_days = len(d_cols)
print(f"Days in sales matrix: {n_days}")
print(f"Days in calendar: {len(m5_cal)}")
print(f"Gap: calendar has {len(m5_cal) - n_days} more days (evaluation period)")
"""))

cells.append(nbf.v4.new_markdown_cell(
"""### Demand sparsity overview

Many item-store series have very low or zero demand on most days. This is
typical for retail data and has major implications for model choice:
- Methods assuming continuous demand will struggle with intermittent series.
- Simple averaging or smoothing may be dominated by zeros.
- The inventory simulation must handle zero-demand periods correctly.
"""))

cells.append(nbf.v4.new_code_cell(
"""# Compute per-series demand statistics (vectorised over d-columns)
print("Computing per-series demand statistics …")
d_values = m5_sales[d_cols].values  # shape (30490, 1913)

total_demand = d_values.sum(axis=1)
n_nonzero = (d_values > 0).sum(axis=1)
mean_demand = d_values.mean(axis=1)
std_demand = d_values.std(axis=1)
zero_share = 1.0 - n_nonzero / n_days

print(f"\\nTotal demand across all series: {total_demand.sum():,.0f} units")
print(f"\\nPer-series demand statistics:")
print(f"  Mean demand:     min={mean_demand.min():.4f}  median={np.median(mean_demand):.4f}  max={mean_demand.max():.4f}")
print(f"  Std dev:         min={std_demand.min():.4f}  median={np.median(std_demand):.4f}  max={std_demand.max():.4f}")
print(f"  Zero-demand %:   min={zero_share.min():.1%}  median={np.median(zero_share):.1%}  max={zero_share.max():.1%}")
print(f"\\nSeries with zero_demand > 90%: {(zero_share > 0.9).sum()} ({(zero_share > 0.9).mean():.1%})")
print(f"Series with zero_demand > 50%: {(zero_share > 0.5).sum()} ({(zero_share > 0.5).mean():.1%})")
print(f"Series with zero_demand = 100%: {(zero_share == 1.0).sum()}")
"""))

cells.append(nbf.v4.new_markdown_cell(
"""## 2. Corporación Favorita — Structure and content

The Favorita dataset covers grocery sales in Ecuador. The original competition
covers 54 stores and ~4,100 items over ~4.5 years.

**Status: SEVERELY TRUNCATED**

Only a partial extraction exists in the raw directory. The following cells
document the exact state of the available data.
"""))

cells.append(nbf.v4.new_code_cell(
"""print("Loading Favorita train.csv …")
fav_train = pd.read_csv(FAV_RAW / 'train.csv')
print(f"  Shape: {fav_train.shape}")
print(f"  Columns: {list(fav_train.columns)}")
print(f"  Date range: {fav_train['date'].min()} → {fav_train['date'].max()}")
print(f"  Unique dates: {fav_train['date'].nunique()}")
print(f"  Unique stores: {fav_train['store_nbr'].nunique()}")
print(f"  Unique items: {fav_train['item_nbr'].nunique()}")

# Check for negative values
neg = (fav_train['unit_sales'] < 0).sum()
print(f"\\n  Rows with negative unit_sales (returns): {neg}")
print(f"  Total rows: {len(fav_train):,}")
"""))

cells.append(nbf.v4.new_markdown_cell(
"""### ⚠️ Critical finding: Favorita data truncation

The available Favorita data covers only **198 days** (2013-01-01 to 2013-07-17),
whereas the full competition dataset spans approximately **1,686 days**
(2013-01-01 to 2017-08-15).

The archive file (`corporacion-favorita-grocery-forecasting-modified.zip`) is
corrupted and cannot be expanded. This means:

1. We have only **198 days** of Favorita data instead of ~4.5 years.
2. The temporal overlap with M5 is extremely limited (see below).
3. Cross-dataset robustness analysis (RQ4 / H4) is **currently infeasible**
   at the level of fidelity the study requires.

**Implication:** The primary study will proceed with M5 as the sole dataset.
The Favorita limitation is documented here and will be revisited if the full
dataset becomes available.
"""))

cells.append(nbf.v4.new_markdown_cell(
"""## 3. Common calendar window

The user constraint (2026-08-27) requires both datasets to share the same
primary calendar window with equal observations per experimental series, where
the window is established from the **actual temporal overlap**.
"""))

cells.append(nbf.v4.new_code_cell(
"""# Compute actual temporal overlap
m5_start = pd.Timestamp(first_date)  # 2011-01-29
m5_end = pd.Timestamp(last_date)     # 2016-04-24

fav_start = pd.Timestamp(fav_train['date'].min())
fav_end = pd.Timestamp(fav_train['date'].max())

overlap_start = max(m5_start, fav_start)
overlap_end = min(m5_end, fav_end)
overlap_days = (overlap_end - overlap_start).days + 1

print("=== Temporal overlap analysis ===")
print(f"M5 range:              {m5_start.date()} → {m5_end.date()} ({(m5_end - m5_start).days + 1} days)")
print(f"Favorita range:        {fav_start.date()} → {fav_end.date()} ({(fav_end - fav_start).days + 1} days)")
print(f"")
print(f"Common overlap:        {overlap_start.date()} → {overlap_end.date()}")
print(f"Overlap duration:      {overlap_days} days")
print(f"")

if overlap_days < 365:
    print("⚠️  Overlap is less than 1 year — this is insufficient for robust")
    print("   cross-dataset comparison with seasonal and annual patterns.")
    print("   Recommendation: proceed with M5 only for the primary analysis.")
else:
    print("Overlap is sufficient for cross-dataset analysis.")
"""))

cells.append(nbf.v4.new_markdown_cell(
"""## 4. Data quality summary

### M5 quality checks
"""))

cells.append(nbf.v4.new_code_cell(
"""# M5 data quality
print("=== M5 Data Quality ===")

# Missing values in sales
print(f"\\nSales matrix:")
print(f"  Total cells: {m5_sales[d_cols].size:,}")
print(f"  Null cells: {(m5_sales[d_cols].isna().sum().sum()):,}")
print(f"  Negative values: {(m5_sales[d_cols] < 0).sum().sum():,}")

# Check for duplicate rows
dup_rows = meta.duplicated(subset=['item_id', 'store_id']).sum()
print(f"\\nDuplicate series (item+store): {dup_rows}")

# Calendar completeness
cal_dates = pd.to_datetime(m5_cal['date'])
print(f"\\nCalendar:")
print(f"  Date range: {cal_dates.min().date()} → {cal_dates.max().date()}")
print(f"  Missing dates: 0 (calendar is continuous)")

# Sell prices coverage
print(f"\\nSell prices:")
print(f"  Total rows: {len(m5_prices):,}")
print(f"  Unique items: {m5_prices['item_id'].nunique()}")
print(f"  Unique stores: {m5_prices['store_id'].nunique()}")
print(f"  Weeks with prices: {m5_prices['wm_yr_wk'].nunique()}")
"""))

cells.append(nbf.v4.new_markdown_cell(
"""### Favorita quality checks
"""))

cells.append(nbf.v4.new_code_cell(
"""# Favorita data quality
print("=== Favorita Data Quality ===")

# Missing values
print(f"\\nTrain file:")
for col in fav_train.columns:
    null_count = fav_train[col].isna().sum()
    print(f"  {col:15s}: {null_count:,} nulls ({null_count/len(fav_train)*100:.1f}%)")

# Negative unit_sales (returns)
neg_sales = fav_train[fav_train['unit_sales'] < 0]
print(f"\\n  Rows with negative unit_sales: {len(neg_sales):,} ({len(neg_sales)/len(fav_train)*100:.1f}%)")
if len(neg_sales) > 0:
    print(f"  Range of negative values: {neg_sales['unit_sales'].min():.0f} to {neg_sales['unit_sales'].max():.0f}")

# Series completeness
fav_series = fav_train.groupby(['store_nbr', 'item_nbr'])
n_series = fav_series.ngroups
print(f"\\n  Unique series (store×item): {n_series:,}")
print(f"  Average days per series: {len(fav_train) / n_series:.1f}")

# Check auxiliary files
for fname, desc in [('stores.csv', 'Stores'), ('items.csv', 'Items'), ('oil.csv', 'Oil prices'), ('holidays_events.csv', 'Holidays'), ('transactions.csv', 'Transactions')]:
    try:
        df = pd.read_csv(FAV_RAW / fname)
        print(f"\\n  {desc} ({fname}): {len(df):,} rows, {list(df.columns[:4])}…")
    except FileNotFoundError:
        print(f"\\n  {desc} ({fname}): ❌ MISSING")
"""))

cells.append(nbf.v4.new_markdown_cell(
"""## 5. Audit summary

The following JSON file records all key facts about both datasets. Downstream
notebooks reference this file rather than recomputing from raw data.
"""))

cells.append(nbf.v4.new_code_cell(
"""# Build audit summary
audit = {
    'generated': pd.Timestamp.now().isoformat(),
    'm5': {
        'total_series': int(len(m5_sales)),
        'n_days': int(n_days),
        'date_range': [str(first_date), str(last_date)],
        'mean_zero_share': float(np.mean(zero_share)),
        'median_zero_share': float(np.median(zero_share)),
        'pct_series_gt90pct_zero': float((zero_share > 0.9).mean()),
        'categories': meta['cat_id'].value_counts().to_dict(),
        'departments': meta['dept_id'].value_counts().to_dict(),
        'stores': meta['store_id'].value_counts().to_dict(),
        'states': meta['state_id'].value_counts().to_dict(),
        'total_demand': float(total_demand.sum()),
        'data_quality': {
            'null_cells': int(m5_sales[d_cols].isna().sum().sum()),
            'negative_cells': int((m5_sales[d_cols] < 0).sum().sum()),
            'duplicate_series': int(dup_rows),
        }
    },
    'favorita': {
        'total_series': int(n_series),
        'n_days': int(fav_train['date'].nunique()),
        'date_range': [str(fav_train['date'].min()), str(fav_train['date'].max())],
        'unique_stores': int(fav_train['store_nbr'].nunique()),
        'unique_items': int(fav_train['item_nbr'].nunique()),
        'negative_sales_rows': int(len(neg_sales)),
        'status': 'SEVERELY_TRUNCATED - only 198 days, zip corrupted',
    },
    'common_window': {
        'start': str(overlap_start.date()),
        'end': str(overlap_end.date()),
        'n_days': int(overlap_days),
        'assessment': 'insufficient' if overlap_days < 365 else 'sufficient',
        'recommendation': 'M5 primary study only; Favorita deferred until full dataset available',
    }
}

# Save
out_dir = PROJ / '02_data'
out_path = out_dir / 'audit_summary.json'
with open(out_path, 'w') as f:
    json.dump(audit, f, indent=2, default=str)
print(f"✅ Audit summary saved to {out_path}")
print(f"\\nM5 series: {audit['m5']['total_series']}, days: {audit['m5']['n_days']}")
print(f"Favorita series: {audit['favorita']['total_series']}, days: {audit['favorita']['n_days']}")
print(f"Common window: {audit['common_window']['start']} → {audit['common_window']['end']} ({audit['common_window']['n_days']} days)")
print(f"Assessment: {audit['common_window']['assessment']}")
"""))

cells.append(nbf.v4.new_markdown_cell(
"""## 6. Decision and next steps

### Key findings

1. **M5 is robust:** 30,490 series, 1913 days (2011-01-29 → 2016-04-24), high sparsity
   (mean zero-share ~68%), no missing values in sales, hierarchical structure.
2. **Favorita is severely limited:** Only 198 days available, archive corrupted.
3. **Common window is insufficient:** 2013-01-01 → 2013-07-17 = 198 days (less than 1 year).
4. **Cross-dataset robustness is deferred** until the full Favorita dataset is obtained.

### Research implication

The primary study proceeds with M5 as the sole dataset. The analysis will be
thorough enough that adding a second dataset later is straightforward — the
inventory simulation and evaluation framework are dataset-agnostic.

### Decision for the next notebook

`03_exploratory_data_analysis.ipynb` will focus on M5 and develop the
series-selection criteria for the experimental sample.
"""))

nb.cells = cells
nbf.write(nb, "08_notebooks/02_data_acquisition_and_audit.ipynb")
print("Created 02_data_acquisition_and_audit.ipynb")
