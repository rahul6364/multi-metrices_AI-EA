#!/usr/bin/env python3
"""
Compute IEEE research metrics from real detector and research logs.

Reads evaluation and research CSV files produced during experiments and writes
aggregated metrics to results/metrics_summary.csv.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from experiment_config import EXPERIMENTS_DIR, LOGS_DIR, METRICS_DIR, ensure_result_dirs
from utils import validate_csv


def _safe_div(num: float, den: float) -> float:
    """Return a safe floating-point ratio."""
    return float(num / den) if den else 0.0


def _confusion_metrics(true_labels: pd.Series, pred_labels: pd.Series) -> dict:
    """Compute confusion matrix counts and derived classification metrics."""
    tp = int(((true_labels == 1) & (pred_labels == 1)).sum())
    tn = int(((true_labels == 0) & (pred_labels == 0)).sum())
    fp = int(((true_labels == 0) & (pred_labels == 1)).sum())
    fn = int(((true_labels == 1) & (pred_labels == 0)).sum())

    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall)
    accuracy = _safe_div(tp + tn, tp + tn + fp + fn)
    fpr = _safe_div(fp, fp + tn)
    fnr = _safe_div(fn, fn + tp)

    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-score": f1,
        "False Positive Rate": fpr,
        "False Negative Rate": fnr,
        "Detection Rate": recall,
    }


def _resource_reduction(research_df: pd.DataFrame) -> dict:
    """Estimate average CPU/energy reduction after mitigation from real logs."""
    if research_df.empty or "mitigation_action" not in research_df.columns:
        return {
            "Average CPU Reduction": 0.0,
            "Average Energy Reduction": 0.0,
            "Energy Saved Percentage": 0.0,
        }

    mitigated_pods = research_df[research_df["mitigation_action"].astype(str).str.len() > 0]["pod_name"].unique()
    cpu_reductions = []
    energy_reductions = []

    for pod in mitigated_pods:
        pod_df = research_df[research_df["pod_name"] == pod].sort_values("timestamp")
        if len(pod_df) < 2:
            continue
        pre = pod_df.iloc[: max(1, len(pod_df) // 2)]
        post = pod_df.iloc[max(1, len(pod_df) // 2):]
        pre_cpu = pre["cpu_utilization_percent"].mean()
        post_cpu = post["cpu_utilization_percent"].mean()
        pre_energy = pre["energy_consumption_joules"].mean()
        post_energy = post["energy_consumption_joules"].mean()
        cpu_reductions.append(max(pre_cpu - post_cpu, 0.0))
        energy_reductions.append(max(pre_energy - post_energy, 0.0))

    avg_cpu_reduction = float(sum(cpu_reductions) / len(cpu_reductions)) if cpu_reductions else 0.0
    avg_energy_reduction = float(sum(energy_reductions) / len(energy_reductions)) if energy_reductions else 0.0
    pre_energy_total = research_df["energy_consumption_joules"].mean()
    energy_saved_pct = _safe_div(avg_energy_reduction, pre_energy_total) * 100.0 if pre_energy_total else 0.0

    return {
        "Average CPU Reduction": avg_cpu_reduction,
        "Average Energy Reduction": avg_energy_reduction,
        "Energy Saved Percentage": energy_saved_pct,
    }


def _find_input_files(logs_dir: Path, experiments_dir: Path) -> tuple[Path | None, Path | None]:
    """Locate the newest evaluation and research logs from host-side directories."""
    eval_candidates = sorted(logs_dir.glob("**/evaluation.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    eval_candidates += sorted(experiments_dir.glob("**/evaluation.csv"), key=lambda p: p.stat().st_mtime, reverse=True)

    research_candidates = sorted(logs_dir.glob("detection_cycles_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    research_candidates += sorted(
        experiments_dir.glob("**/detection_cycles_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    eval_path = eval_candidates[0] if eval_candidates else None
    research_path = research_candidates[0] if research_candidates else None
    return eval_path, research_path


def calculate_metrics(
    evaluation_csv: Path | None = None,
    research_csv: Path | None = None,
    output_csv: Path | None = None,
) -> pd.DataFrame:
    """
    Compute ML and operational metrics and save them to metrics_summary.csv.

    Returns the metrics DataFrame for downstream plotting.
    """
    ensure_result_dirs()
    eval_path, research_path = _find_input_files(LOGS_DIR, EXPERIMENTS_DIR)
    eval_path = evaluation_csv or eval_path
    research_path = research_csv or research_path

    if eval_path is None:
        raise FileNotFoundError("No evaluation.csv found. Run an experiment first.")

    eval_df = validate_csv(
        eval_path,
        required_columns=["true_label", "prediction_ea", "prediction_basic", "timestamp"],
    )

    research_df = pd.DataFrame()
    if research_path and research_path.exists():
        research_df = validate_csv(research_path)

    true_labels = eval_df["true_label"].astype(int)
    pred_ea = eval_df["prediction_ea"].map(lambda value: 1 if value == "ANOMALY" else 0)
    pred_basic = eval_df["prediction_basic"].map(lambda value: 1 if value == "ANOMALY" else 0)

    ea_metrics = _confusion_metrics(true_labels, pred_ea)
    basic_metrics = _confusion_metrics(true_labels, pred_basic)

    first_attack = eval_df.loc[eval_df["true_label"] == 1, "timestamp"].min()
    first_ea = eval_df.loc[(eval_df["true_label"] == 1) & (eval_df["prediction_ea"] == "ANOMALY"), "timestamp"].min()
    first_basic = eval_df.loc[
        (eval_df["true_label"] == 1) & (eval_df["prediction_basic"] == "ANOMALY"),
        "timestamp",
    ].min()

    ea_detection_latency = float(first_ea - first_attack) if pd.notna(first_attack) and pd.notna(first_ea) else -1.0
    basic_detection_latency = (
        float(first_basic - first_attack) if pd.notna(first_attack) and pd.notna(first_basic) else -1.0
    )

    avg_detection_latency = ea_detection_latency
    avg_mitigation_latency = -1.0
    if not research_df.empty and "mitigation_latency_ms" in research_df.columns:
        valid = research_df.loc[research_df["mitigation_latency_ms"] >= 0, "mitigation_latency_ms"]
        if not valid.empty:
            avg_mitigation_latency = float(valid.mean() / 1000.0)
        valid_detection = research_df.loc[research_df["detection_latency_ms"] >= 0, "detection_latency_ms"]
        if not valid_detection.empty:
            avg_detection_latency = float(valid_detection.mean() / 1000.0)

    resource_metrics = _resource_reduction(research_df)

    rows = []
    for model_name, metrics, detection_latency in [
        ("Energy-Aware", ea_metrics, ea_detection_latency),
        ("Basic IF", basic_metrics, basic_detection_latency),
    ]:
        row = {"Model": model_name, **metrics}
        row["Average Detection Latency (s)"] = detection_latency
        row["Average Mitigation Latency (s)"] = avg_mitigation_latency
        row.update(resource_metrics)
        rows.append(row)

    summary_df = pd.DataFrame(rows)
    output_path = output_csv or (METRICS_DIR / "metrics_summary.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_path, index=False)

    root_summary = output_path.parent.parent / "metrics_summary.csv"
    summary_df.to_csv(root_summary, index=False)
    print(f"[OK] Metrics summary saved to {output_path}")
    print(f"[OK] Metrics summary saved to {root_summary}")
    return summary_df


def main() -> None:
    """CLI entry point for metrics calculation."""
    parser = argparse.ArgumentParser(description="Calculate IEEE experiment metrics")
    parser.add_argument("--evaluation-csv", default="")
    parser.add_argument("--research-csv", default="")
    parser.add_argument("--output-csv", default="")
    args = parser.parse_args()

    calculate_metrics(
        evaluation_csv=Path(args.evaluation_csv) if args.evaluation_csv else None,
        research_csv=Path(args.research_csv) if args.research_csv else None,
        output_csv=Path(args.output_csv) if args.output_csv else None,
    )


if __name__ == "__main__":
    main()
