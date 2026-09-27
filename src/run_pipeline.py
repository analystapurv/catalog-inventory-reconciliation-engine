"""
run_pipeline.py
Runs the full Catalog & Inventory Reconciliation pipeline end to end:
  1. Load real catalog + derive ERP/WMS exports (load_and_derive.py)
  2. Reconcile exports against ground truth (reconcile.py)
  3. Print summary metrics and save all outputs to results/
"""

from load_and_derive import load_ground_truth, derive_erp_export, derive_wms_export
from reconcile import reconcile, summarize
import os

os.makedirs("../results", exist_ok=True)

print("Step 1/3: Loading real Flipkart catalog and deriving ERP/WMS exports...")
gt = load_ground_truth()
erp = derive_erp_export(gt)
wms = derive_wms_export(gt)
gt.to_csv("../results/ground_truth_catalog.csv", index=False)
erp.to_csv("../results/erp_export.csv", index=False)
wms.to_csv("../results/wms_export.csv", index=False)
print(f"  Ground truth: {len(gt)} SKUs | ERP export: {len(erp)} SKUs | WMS export: {len(wms)} SKUs")

print("\nStep 2/3: Reconciling exports against ground truth...")
report = reconcile(gt, erp, wms)
stats = summarize(report)

print("\nStep 3/3: Results")
print("=== RECONCILIATION SUMMARY ===")
for k, v in stats.items():
    pct = f" ({100*v/stats['total_skus']:.2f}%)" if k != "total_skus" else ""
    print(f"{k}: {v}{pct}")

report.to_csv("../results/reconciliation_report.csv", index=False)
gt.to_csv("../results/corrected_master_catalog.csv", index=False)
print("\nSaved all outputs to results/")
