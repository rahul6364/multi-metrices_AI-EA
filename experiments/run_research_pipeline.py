#!/usr/bin/env python3
"""
Single-command orchestrator for the IEEE research evaluation pipeline.

Runs metric export, experiments, log collection, metrics calculation, and
graph generation in sequence using only real cluster data.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from experiment_config import LOGS_DIR, RAW_METRICS_DIR, SCENARIO_MAP, ensure_result_dirs
from export_metrics import export_metrics
from calculate_metrics import calculate_metrics
from generate_graphs import generate_graphs
from run_experiment import run_experiment
from utils import copy_detector_logs


def sync_logs_to_results(experiment_dir: Path) -> None:
    """Copy the latest experiment logs into the centralized results/logs directory."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    source = experiment_dir / "detector_logs"
    if not source.exists():
        return

    for item in source.rglob("*"):
        if item.is_file():
            target = LOGS_DIR / item.name
            if target.exists():
                stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                target = LOGS_DIR / f"{item.stem}_{stamp}{item.suffix}"
            shutil.copy2(item, target)

    research_dir = source / "research"
    if research_dir.exists() and research_dir.is_dir():
        for csv_file in research_dir.glob("*.csv"):
            target = LOGS_DIR / csv_file.name
            if target.exists():
                stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                target = LOGS_DIR / f"{csv_file.stem}_{stamp}{csv_file.suffix}"
            shutil.copy2(csv_file, target)


def run_pipeline(
    scenarios: list[str],
    skip_export: bool = False,
    skip_experiments: bool = False,
    skip_metrics: bool = False,
    skip_graphs: bool = False,
) -> None:
    """Execute the full research pipeline for one or more scenarios."""
    ensure_result_dirs()
    experiment_dirs: list[Path] = []

    if not skip_export:
        print("\n=== Step 1: Export Prometheus / Kepler metrics ===")
        export_metrics(RAW_METRICS_DIR)

    if not skip_experiments:
        print("\n=== Step 2: Run experiments ===")
        for scenario in scenarios:
            experiment_dir = run_experiment(scenario)
            sync_logs_to_results(experiment_dir)
            experiment_dirs.append(experiment_dir)
    else:
        print("\n=== Step 2: Skipped experiment execution ===")

    if not skip_metrics:
        print("\n=== Step 3: Calculate ML metrics ===")
        calculate_metrics()

    if not skip_graphs:
        print("\n=== Step 4: Generate IEEE figures ===")
        generate_graphs()

    print("\n=== Pipeline complete ===")
    if experiment_dirs:
        print("Experiment outputs:")
        for path in experiment_dirs:
            print(f"  - {path}")


def main() -> None:
    """CLI entry point for the full research pipeline."""
    parser = argparse.ArgumentParser(description="Run the complete IEEE research pipeline")
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=["cpu"],
        choices=list(SCENARIO_MAP.keys()),
        help="One or more experiment scenarios to execute",
    )
    parser.add_argument("--all-scenarios", action="store_true", help="Run every supported scenario")
    parser.add_argument("--skip-export", action="store_true")
    parser.add_argument("--skip-experiments", action="store_true")
    parser.add_argument("--skip-metrics", action="store_true")
    parser.add_argument("--skip-graphs", action="store_true")
    args = parser.parse_args()

    scenarios = list(SCENARIO_MAP.keys()) if args.all_scenarios else args.scenarios

    try:
        run_pipeline(
            scenarios=scenarios,
            skip_export=args.skip_export,
            skip_experiments=args.skip_experiments,
            skip_metrics=args.skip_metrics,
            skip_graphs=args.skip_graphs,
        )
    except Exception as exc:
        print(f"[ERROR] Pipeline failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
