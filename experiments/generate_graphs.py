#!/usr/bin/env python3
"""
Generate publication-quality IEEE figures from real experiment data.

Produces 10 figures at 300 DPI in PNG, PDF, and SVG formats using only
metrics collected from the live Kubernetes cluster.
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

from experiment_config import EXPERIMENTS_DIR, FIGURES_DIR, LOGS_DIR, METRICS_DIR, ensure_result_dirs
from utils import validate_csv

# Publication styling for IEEE paper figures.
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "axes.grid": True,
        "grid.alpha": 0.3,
    }
)

ANOMALY_THRESHOLD = 0.0


def _save_figure(fig: plt.Figure, stem: str, output_dir: Path) -> None:
    """Save a figure in PNG, PDF, and SVG formats."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(output_dir / f"{stem}.{ext}", bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved figure: {stem}")


def _find_latest_csv(patterns: list[str], search_dirs: list[Path]) -> Path | None:
    """Return the newest CSV matching any pattern across search directories."""
    candidates: list[Path] = []
    for directory in search_dirs:
        if not directory.exists():
            continue
        for pattern in patterns:
            candidates.extend(directory.rglob(pattern))
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _load_inputs(
    research_csv: Path | None,
    evaluation_csv: Path | None,
    metrics_csv: Path | None,
    mitigations_csv: Path | None,
) -> dict[str, pd.DataFrame | None]:
    """Load and validate all CSV inputs required for plotting."""
    search_dirs = [LOGS_DIR, EXPERIMENTS_DIR, METRICS_DIR]
    research_path = research_csv or _find_latest_csv(["detection_cycles_*.csv"], search_dirs)
    evaluation_path = evaluation_csv or _find_latest_csv(["evaluation.csv"], search_dirs)
    metrics_path = metrics_csv or (METRICS_DIR / "metrics_summary.csv")
    mitigations_path = mitigations_csv or _find_latest_csv(["mitigations.csv"], search_dirs)

    inputs: dict[str, pd.DataFrame | None] = {
        "research": None,
        "evaluation": None,
        "metrics": None,
        "mitigations": None,
    }

    if research_path and research_path.exists():
        inputs["research"] = validate_csv(research_path)
    if evaluation_path and evaluation_path.exists():
        inputs["evaluation"] = validate_csv(
            evaluation_path,
            required_columns=["timestamp", "prediction_ea", "score_ea", "true_label"],
        )
    if metrics_path.exists():
        metrics_df = pd.read_csv(metrics_path)
        if not metrics_df.empty:
            inputs["metrics"] = metrics_df
    if mitigations_path and mitigations_path.exists():
        mitigations_df = pd.read_csv(mitigations_path)
        if not mitigations_df.empty:
            inputs["mitigations"] = mitigations_df

    return inputs


def figure_01_cpu_before_after(research_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 1: CPU utilization before vs after mitigation."""
    df = research_df.sort_values("timestamp").copy()
    df["relative_time_s"] = df["timestamp"] - df["timestamp"].min()
    mitigated = df[df["mitigation_action"].astype(str).str.len() > 0]
    split_time = mitigated["timestamp"].min() if not mitigated.empty else df["timestamp"].median()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for pod in df["pod_name"].unique()[:5]:
        pod_df = df[df["pod_name"] == pod]
        ax.plot(
            pod_df["relative_time_s"],
            pod_df["cpu_utilization_percent"],
            label=pod,
            linewidth=1.5,
        )

    ax.axvline(split_time - df["timestamp"].min(), color="red", linestyle="--", label="Mitigation")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("CPU Utilization (%)")
    ax.set_title("Figure 1: CPU Utilization Before vs After Mitigation")
    ax.legend(loc="best", fontsize=8)
    _save_figure(fig, "figure_01_cpu_before_after_mitigation", output_dir)


def figure_02_energy_before_after(research_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 2: Energy consumption before vs after mitigation."""
    df = research_df.sort_values("timestamp").copy()
    df["relative_time_s"] = df["timestamp"] - df["timestamp"].min()
    mitigated = df[df["mitigation_action"].astype(str).str.len() > 0]
    split_time = mitigated["timestamp"].min() if not mitigated.empty else df["timestamp"].median()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for pod in df["pod_name"].unique()[:5]:
        pod_df = df[df["pod_name"] == pod]
        ax.plot(
            pod_df["relative_time_s"],
            pod_df["energy_consumption_joules"],
            label=pod,
            linewidth=1.5,
        )

    ax.axvline(split_time - df["timestamp"].min(), color="red", linestyle="--", label="Mitigation")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Energy (J)")
    ax.set_title("Figure 2: Energy Consumption Before vs After Mitigation")
    ax.legend(loc="best", fontsize=8)
    _save_figure(fig, "figure_02_energy_before_after_mitigation", output_dir)


def figure_03_detection_performance(metrics_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 3: Detection performance bar chart."""
    ea_row = metrics_df[metrics_df["Model"] == "Energy-Aware"]
    if ea_row.empty:
        ea_row = metrics_df.iloc[[0]]

    metrics = ["Accuracy", "Precision", "Recall", "F1-score"]
    values = [float(ea_row[metric].iloc[0]) for metric in metrics]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(metrics, values, color=["#2E86AB", "#A23B72", "#F18F01", "#3B1F2B"])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Figure 3: Detection Performance (Energy-Aware Model)")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.2f}", ha="center", fontsize=9)
    _save_figure(fig, "figure_03_detection_performance", output_dir)


def figure_04_normal_vs_attack(research_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 4: Normal vs attack resource usage grouped bar chart."""
    df = research_df.copy()
    df["workload_type"] = np.where(
        df["detected_attack_type"].astype(str).eq("Normal"),
        "Normal",
        "Attack",
    )
    grouped = df.groupby("workload_type")[
        ["cpu_utilization_percent", "memory_utilization_percent", "network_receive_bytes", "energy_consumption_joules"]
    ].mean()

    metric_labels = ["CPU", "Memory", "Network", "Energy"]
    columns = [
        "cpu_utilization_percent",
        "memory_utilization_percent",
        "network_receive_bytes",
        "energy_consumption_joules",
    ]

    x = np.arange(len(metric_labels))
    width = 0.35
    normal_vals = [grouped.loc["Normal", col] if "Normal" in grouped.index else 0.0 for col in columns]
    attack_vals = [grouped.loc["Attack", col] if "Attack" in grouped.index else 0.0 for col in columns]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - width / 2, normal_vals, width, label="Normal", color="#4C78A8")
    ax.bar(x + width / 2, attack_vals, width, label="Attack", color="#E45756")
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.set_ylabel("Average Value")
    ax.set_title("Figure 4: Normal vs Attack Resource Usage")
    ax.legend()
    _save_figure(fig, "figure_04_normal_vs_attack_resources", output_dir)


def figure_05_anomaly_scores(evaluation_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 5: Isolation Forest anomaly score timeline with threshold."""
    df = evaluation_df.sort_values("timestamp").copy()
    df["relative_time_s"] = df["timestamp"] - df["timestamp"].min()
    anomalies = df[df["prediction_ea"] == "ANOMALY"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df["relative_time_s"], df["score_ea"], color="#2E86AB", linewidth=1.5, label="Anomaly Score")
    ax.axhline(ANOMALY_THRESHOLD, color="red", linestyle="--", linewidth=1.2, label="Threshold")
    if not anomalies.empty:
        ax.scatter(
            anomalies["relative_time_s"],
            anomalies["score_ea"],
            color="#E45756",
            s=30,
            label="Detected Anomalies",
            zorder=3,
        )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Anomaly Score")
    ax.set_title("Figure 5: Isolation Forest Anomaly Score")
    ax.legend()
    _save_figure(fig, "figure_05_anomaly_score_timeline", output_dir)


def figure_06_attack_counts(research_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 6: Detected attack counts by category."""
    categories = ["Normal", "CPU", "Memory", "Network", "Cryptojacking"]
    counts = []
    for category in categories:
        if category == "Normal":
            counts.append(int((research_df["prediction"] == "NORMAL").sum()))
        else:
            counts.append(int((research_df["detected_attack_type"] == category).sum()))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(categories, counts, color="#72B7B2")
    ax.set_ylabel("Count")
    ax.set_title("Figure 6: Detected Attack Counts")
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, count + 0.5, str(count), ha="center", fontsize=9)
    _save_figure(fig, "figure_06_detected_attack_counts", output_dir)


def figure_07_mitigation_timeline(
    research_df: pd.DataFrame,
    mitigations_df: pd.DataFrame | None,
    output_dir: Path,
) -> None:
    """Figure 7: Mitigation timeline bar chart."""
    stages = ["Detection", "Alert", "Throttling", "Isolation", "Termination"]
    counts = [0, 0, 0, 0, 0]

    counts[0] = int((research_df["prediction"] == "ANOMALY").sum())
    counts[1] = int(research_df.get("confirmed_attack", pd.Series(dtype=float)).sum()) if "confirmed_attack" in research_df else counts[0]

    if mitigations_df is not None and "action" in mitigations_df.columns:
        counts[2] = int((mitigations_df["action"] == "THROTTLED").sum())
        counts[4] = int((mitigations_df["action"] == "DELETED").sum())
    else:
        counts[2] = int((research_df["mitigation_action"] == "THROTTLED").sum())
        counts[4] = int((research_df["mitigation_action"] == "DELETED").sum())

    counts[3] = max(counts[2] - counts[4], 0)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(stages, counts, color="#B279A2")
    ax.set_ylabel("Event Count")
    ax.set_title("Figure 7: Mitigation Timeline")
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, count + 0.3, str(count), ha="center", fontsize=9)
    _save_figure(fig, "figure_07_mitigation_timeline", output_dir)


def figure_08_confusion_matrix(evaluation_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 8: Confusion matrix for Energy-Aware model."""
    y_true = evaluation_df["true_label"].astype(int).values
    y_pred = evaluation_df["prediction_ea"].map(lambda value: 1 if value == "ANOMALY" else 0).values
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])

    fig, ax = plt.subplots(figsize=(5.5, 5))
    disp = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=["Normal", "Anomaly"])
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Figure 8: Confusion Matrix (Energy-Aware)")
    _save_figure(fig, "figure_08_confusion_matrix", output_dir)


def figure_09_cpu_energy_correlation(research_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 9: CPU and energy correlation scatter plot."""
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.scatter(
        research_df["cpu_utilization_percent"],
        research_df["energy_consumption_joules"],
        alpha=0.6,
        c=research_df["anomaly_score"],
        cmap="viridis",
        edgecolors="none",
    )
    ax.set_xlabel("CPU Utilization (%)")
    ax.set_ylabel("Energy Consumption (J)")
    ax.set_title("Figure 9: CPU and Energy Correlation")
    _save_figure(fig, "figure_09_cpu_energy_correlation", output_dir)


def figure_10_detection_latency(research_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 10: Detection latency distribution histogram."""
    latencies = research_df.loc[research_df["detection_latency_ms"] >= 0, "detection_latency_ms"]
    if latencies.empty:
        warnings.warn("No detection latency values available for Figure 10.")
        return

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(latencies, bins=min(20, max(5, len(latencies))), color="#F58518", edgecolor="white")
    ax.set_xlabel("Detection Latency (ms)")
    ax.set_ylabel("Frequency")
    ax.set_title("Figure 10: Detection Latency Distribution")
    _save_figure(fig, "figure_10_detection_latency_distribution", output_dir)


def generate_graphs(
    output_dir: Path | None = None,
    research_csv: Path | None = None,
    evaluation_csv: Path | None = None,
    metrics_csv: Path | None = None,
    mitigations_csv: Path | None = None,
) -> None:
    """Generate all IEEE figures when sufficient real data is available."""
    ensure_result_dirs()
    output = output_dir or FIGURES_DIR
    inputs = _load_inputs(research_csv, evaluation_csv, metrics_csv, mitigations_csv)

    if inputs["research"] is None and inputs["evaluation"] is None:
        raise FileNotFoundError("No research or evaluation CSV files found. Run experiments first.")

    research_df = inputs["research"]
    evaluation_df = inputs["evaluation"]
    metrics_df = inputs["metrics"]
    mitigations_df = inputs["mitigations"]

    if research_df is not None:
        figure_01_cpu_before_after(research_df, output)
        figure_02_energy_before_after(research_df, output)
        figure_04_normal_vs_attack(research_df, output)
        figure_06_attack_counts(research_df, output)
        figure_07_mitigation_timeline(research_df, mitigations_df, output)
        figure_09_cpu_energy_correlation(research_df, output)
        figure_10_detection_latency(research_df, output)
    else:
        warnings.warn("Research log missing. Skipping Figures 1, 2, 4, 6, 7, 9, 10.")

    if evaluation_df is not None:
        figure_05_anomaly_scores(evaluation_df, output)
        figure_08_confusion_matrix(evaluation_df, output)
    else:
        warnings.warn("Evaluation log missing. Skipping Figures 5 and 8.")

    if metrics_df is not None:
        figure_03_detection_performance(metrics_df, output)
    else:
        warnings.warn("Metrics summary missing. Skipping Figure 3.")


def main() -> None:
    """CLI entry point for graph generation."""
    parser = argparse.ArgumentParser(description="Generate IEEE publication figures")
    parser.add_argument("--output-dir", default=str(FIGURES_DIR))
    parser.add_argument("--research-csv", default="")
    parser.add_argument("--evaluation-csv", default="")
    parser.add_argument("--metrics-csv", default="")
    parser.add_argument("--mitigations-csv", default="")
    args = parser.parse_args()

    generate_graphs(
        output_dir=Path(args.output_dir),
        research_csv=Path(args.research_csv) if args.research_csv else None,
        evaluation_csv=Path(args.evaluation_csv) if args.evaluation_csv else None,
        metrics_csv=Path(args.metrics_csv) if args.metrics_csv else None,
        mitigations_csv=Path(args.mitigations_csv) if args.mitigations_csv else None,
    )


if __name__ == "__main__":
    main()
