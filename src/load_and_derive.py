"""
load_and_derive.py
Loads the real Flipkart product catalog (ground truth) and generates two
derived exports simulating how an ERP and a WMS naturally drift out of sync
with the source catalog over time in a real company:
  - ERP export: stale prices (weekly batch sync lag) + a few SKUs not yet
    onboarded
  - WMS export: manual stock-count overrides + a few listing name edits
    made directly in the warehouse system

All drift is applied ON TOP of real product records -- prices, names, and
product IDs are 100% real. Only the 'stock' field is synthetic (the Flipkart
dataset has no stock column), and that is disclosed here rather than hidden.
"""

import pandas as pd
import numpy as np

RAW_PATH = RAW_PATH = "C:/Data engineer/Group B/project2/data/flipkart_com-ecommerce_sample.csv"
SEED = 42


def load_ground_truth(path: str = RAW_PATH) -> pd.DataFrame:
    """Load and clean the real catalog into the ground-truth reference table."""
    df = pd.read_csv(path)
    df = df.dropna(subset=["pid", "retail_price", "discounted_price", "product_name"]).copy()
    df = df.drop_duplicates(subset=["pid"], keep="first")
    df["retail_price"] = df["retail_price"].astype(float)
    df["discounted_price"] = df["discounted_price"].astype(float)

    np.random.seed(SEED)
    ground_truth = df[["pid", "product_name", "discounted_price"]].copy()
    ground_truth["stock"] = np.random.randint(0, 200, size=len(ground_truth))  # disclosed synthetic field
    return ground_truth.reset_index(drop=True)


def derive_erp_export(ground_truth: pd.DataFrame) -> pd.DataFrame:
    """Simulate an ERP export: ~12% stale prices, ~3% SKUs not yet onboarded."""
    n = len(ground_truth)
    erp = ground_truth.copy()

    stale_idx = np.random.choice(n, size=int(n * 0.12), replace=False)
    erp.loc[stale_idx, "discounted_price"] = (
        erp.loc[stale_idx, "discounted_price"] * np.random.uniform(0.85, 1.15, len(stale_idx))
    ).round(2)

    missing_idx = np.random.choice(n, size=int(n * 0.03), replace=False)
    erp = erp.drop(index=missing_idx).reset_index(drop=True)
    return erp


def derive_wms_export(ground_truth: pd.DataFrame) -> pd.DataFrame:
    """Simulate a WMS export: ~20% manual stock drift, ~2% listing name edits."""
    n = len(ground_truth)
    wms = ground_truth.copy()

    stock_idx = np.random.choice(n, size=int(n * 0.20), replace=False)
    wms.loc[stock_idx, "stock"] = (
        wms.loc[stock_idx, "stock"] + np.random.randint(-15, 15, len(stock_idx))
    ).clip(lower=0)

    name_idx = np.random.choice(n, size=int(n * 0.02), replace=False)
    wms.loc[name_idx, "product_name"] = wms.loc[name_idx, "product_name"].str[:40] + " (WMS-EDIT)"
    return wms


if __name__ == "__main__":
    gt = load_ground_truth()
    erp = derive_erp_export(gt)
    wms = derive_wms_export(gt)
    gt.to_csv("../results/ground_truth_catalog.csv", index=False)
    erp.to_csv("../results/erp_export.csv", index=False)
    wms.to_csv("../results/wms_export.csv", index=False)
    print(f"Ground truth: {len(gt)} SKUs | ERP export: {len(erp)} SKUs | WMS export: {len(wms)} SKUs")
