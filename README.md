# Catalog & Inventory Reconciliation Engine

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.2-black)
![Status](https://img.shields.io/badge/status-validated-brightgreen)

A reconciliation engine that compares a real product catalog against
simulated ERP and WMS exports to detect price, stock, and listing drift —
the kind of catalog inconsistency that causes overselling, pricing errors,
and customer-facing listing mismatches in real e-commerce operations.

## Dataset
[Flipkart Products Dataset](https://www.kaggle.com/datasets/PromptCloudHQ/flipkart-products)
by PromptCloudHQ — **19,920 real products** (after cleaning) used as ground truth.

## Problem statement
In real e-commerce operations, the same product catalog lives in multiple
systems — an ERP for pricing/finance, a WMS for warehouse stock, and the
storefront itself. These systems sync on different schedules and are
sometimes edited manually, so they drift out of sync: prices go stale,
stock counts diverge, listing names get edited in only one place. This
project simulates that drift on top of a real 19,920-SKU catalog and
builds a reconciliation engine to detect and correct it.

## Architecture
```
Real Flipkart catalog (ground truth)
        │
        ▼
load_and_derive.py ──► erp_export.csv   (12% stale prices, 3% missing SKUs)
        │          └─► wms_export.csv   (20% stock drift, 2% name edits)
        ▼
  reconcile.py ──► reconciliation_report.csv  (per-SKU mismatch flags)
        │      └─► corrected_master_catalog.csv (ground truth wins)
        ▼
   run_pipeline.py  (orchestrates all steps, prints summary)
```

**Important disclosure:** Product IDs, names, and prices are 100% real,
taken directly from the Flipkart dataset. The Flipkart dataset has no
stock field, so `stock` is the one synthetic field in this project —
randomly generated once as ground truth, then deliberately drifted in the
WMS export to simulate real-world stock discrepancies. All drift
percentages (12% stale price, 3% missing, 20% stock drift, 2% name edits)
are fixed, disclosed parameters in the code, not hidden or randomized per
run (seed=42 for full reproducibility).

## Real results (computed by running `run_pipeline.py`)

| Metric | Value |
|---|---|
| Total SKUs in ground truth catalog | 19,920 |
| Missing from ERP export | 597 (3.00%) |
| Price mismatches (ERP vs. ground truth) | 2,328 (11.69%) |
| Stock mismatches (WMS vs. ground truth) | 3,855 (19.35%) |
| Listing name mismatches (WMS vs. ground truth) | 398 (2.00%) |
| **Clean records (fully in sync)** | **13,430 (67.42%)** |
| **Records needing correction** | **6,490 (32.58%)** |

All numbers above are the direct, unedited output of running the code
against the real dataset — see `results/reconciliation_report.csv` for the
full per-SKU breakdown.

## What this demonstrates for an FDE role
- Designing reconciliation logic between systems that don't share a single
  source of truth (a core pattern in OMS/WMS/ERP integrations)
- Building a resolution strategy (ground-truth-wins) rather than just
  flagging problems
- Working with a real, messy dataset (nulls, duplicate IDs) and handling
  it defensively rather than assuming clean input

## How to run it
```bash
pip install -r requirements.txt
cd src
python run_pipeline.py
```
Update the `RAW_PATH` constant in `load_and_derive.py` to point to your
local copy of `flipkart_com-ecommerce_sample.csv` first.

## Project structure
```
src/
  load_and_derive.py   # loads real catalog, derives ERP/WMS exports with drift
  reconcile.py          # compares exports against ground truth, flags mismatches
  run_pipeline.py        # orchestrates the full pipeline end to end
results/
  ground_truth_catalog.csv
  erp_export.csv
  wms_export.csv
  reconciliation_report.csv
  corrected_master_catalog.csv
requirements.txt
```
