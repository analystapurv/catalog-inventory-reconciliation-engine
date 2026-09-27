"""
reconcile.py
Compares the ERP and WMS exports against the ground-truth catalog and flags
price, stock, listing, and coverage mismatches. Produces a per-SKU
reconciliation report and a corrected master catalog (ground truth wins,
since it represents the real source-of-truth product data).
"""

import pandas as pd


def reconcile(ground_truth: pd.DataFrame, erp: pd.DataFrame, wms: pd.DataFrame) -> pd.DataFrame:
    gt = ground_truth.set_index("pid")
    erp_i = erp.set_index("pid")
    wms_i = wms.set_index("pid")

    rows = []
    for pid, truth in gt.iterrows():
        in_erp = pid in erp_i.index
        in_wms = pid in wms_i.index
        row = {"pid": pid, "in_erp": in_erp, "in_wms": in_wms}

        if in_erp:
            price_diff = abs(erp_i.loc[pid, "discounted_price"] - truth["discounted_price"])
            row["price_mismatch"] = bool(price_diff > 0.01)
            row["price_diff_amount"] = round(float(price_diff), 2)
        else:
            row["price_mismatch"] = False
            row["price_diff_amount"] = None

        if in_wms:
            row["stock_mismatch"] = bool(wms_i.loc[pid, "stock"] != truth["stock"])
            row["name_mismatch"] = bool(wms_i.loc[pid, "product_name"] != truth["product_name"])
        else:
            row["stock_mismatch"] = False
            row["name_mismatch"] = False

        rows.append(row)

    return pd.DataFrame(rows)


def summarize(report: pd.DataFrame) -> dict:
    total = len(report)
    clean = (
        report["in_erp"] & report["in_wms"]
        & ~report["price_mismatch"] & ~report["stock_mismatch"] & ~report["name_mismatch"]
    ).sum()

    return {
        "total_skus": total,
        "missing_from_erp": int((~report["in_erp"]).sum()),
        "price_mismatches": int(report["price_mismatch"].sum()),
        "stock_mismatches": int(report["stock_mismatch"].sum()),
        "name_mismatches": int(report["name_mismatch"].sum()),
        "clean_records": int(clean),
        "records_needing_correction": int(total - clean),
    }


if __name__ == "__main__":
    gt = pd.read_csv("../results/ground_truth_catalog.csv")
    erp = pd.read_csv("../results/erp_export.csv")
    wms = pd.read_csv("../results/wms_export.csv")

    report = reconcile(gt, erp, wms)
    stats = summarize(report)

    print("=== RECONCILIATION SUMMARY ===")
    for k, v in stats.items():
        pct = f" ({100*v/stats['total_skus']:.2f}%)" if k != "total_skus" else ""
        print(f"{k}: {v}{pct}")

    report.to_csv("../results/reconciliation_report.csv", index=False)
    gt.to_csv("../results/corrected_master_catalog.csv", index=False)  # ground truth is the correction
    print("\nSaved reconciliation_report.csv and corrected_master_catalog.csv")
