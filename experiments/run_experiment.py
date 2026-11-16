#!/usr/bin/env python3
"""
Automated experiment runner for IEEE evaluation scenarios.

Orchestrates baseline collection, attack deployment, log harvesting, and
metric export for one scenario at a time.
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

from experiment_config import ATTACK_YAMLS, DETECTOR_URL, EXPERIMENTS_DIR, SCENARIO_MAP, ensure_result_dirs
from export_metrics import export_metrics
from utils import (
    apply_workload,
    cleanup_attacks,
    copy_detector_logs,
    detector_get,
    detector_post,
    save_json,
    wait_for_detector_state,
    wait_for_http,
)


def _wait_for_training_complete(timeout_seconds: int = 900) -> None:
    """Wait until baseline training finishes and detection becomes active."""
    wait_for_detector_state("DETECTING", timeout_seconds=timeout_seconds)


def _wait_for_attack_outcome(scenario: str, timeout_seconds: int = 900) -> dict:
    """
    Poll detector APIs until mitigation occurs or timeout expires.

    Returns a summary dictionary describing observed detection/mitigation events.
    """
    deadline = time.time() + timeout_seconds
    summary = {
        "scenario": scenario,
        "confirmed_attack_detected": False,
        "mitigation_observed": False,
        "detection_count": 0,
        "mitigation_count": 0,
    }

    while time.time() < deadline:
        detections = detector_get("/api/detections")
        mitigations = detector_get("/api/mitigations")
        summary["detection_count"] = len(detections)
        summary["mitigation_count"] = len(mitigations)

        if any(item.get("confirmed_attack") for item in detections):
            summary["confirmed_attack_detected"] = True
        if mitigations:
            summary["mitigation_observed"] = True
            if scenario != "normal":
                break
        time.sleep(5)

    return summary


def run_experiment(scenario: str, output_root: Path | None = None) -> Path:
    """
    Execute one end-to-end experiment for the selected scenario.

    Parameters
    ----------
    scenario : str
        One of: normal, cpu, memory, network, combined, cryptojacking.
    output_root : Path | None
        Optional override for experiment output directory.
    """
    if scenario not in SCENARIO_MAP:
        raise ValueError(f"Unsupported scenario '{scenario}'. Choose from {list(SCENARIO_MAP)}")

    ensure_result_dirs()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    experiment_dir = output_root or (EXPERIMENTS_DIR / f"{stamp}_{scenario}")
    experiment_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Starting experiment: {scenario}")
    print(f"[INFO] Output directory: {experiment_dir}")

    wait_for_http(f"{DETECTOR_URL}/api/status")
    cleanup_attacks(ATTACK_YAMLS)

    print("[INFO] Resetting detector logs and starting baseline collection...")
    detector_post("/api/training/start")
    _wait_for_training_complete()

    print("[INFO] Exporting baseline metrics...")
    export_metrics(experiment_dir / "baseline_metrics", namespace="default")

    scenario_cfg = SCENARIO_MAP[scenario]
    if scenario_cfg["attack_yaml"] is not None:
        print(f"[INFO] Deploying attack workload: {scenario_cfg['attack_yaml'].name}")
        apply_workload(scenario_cfg["attack_yaml"])
        time.sleep(20)
    else:
        print("[INFO] Running normal-workload control scenario (no attack deployed).")

    print("[INFO] Collecting attack-phase metrics...")
    export_metrics(experiment_dir / "attack_metrics", namespace="default")

    print("[INFO] Waiting for detection and mitigation events...")
    summary = _wait_for_attack_outcome(scenario)
    save_json(experiment_dir / "experiment_summary.json", summary)

    print("[INFO] Copying detector logs from pod...")
    copy_detector_logs(experiment_dir / "detector_logs")

    print("[INFO] Exporting final Prometheus snapshot...")
    export_metrics(experiment_dir / "final_metrics", namespace="default")

    metadata = {
        "scenario": scenario,
        "label": scenario_cfg["label"],
        "started_at": stamp,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
    }
    save_json(experiment_dir / "metadata.json", metadata)
    print(f"[OK] Experiment complete: {experiment_dir}")
    return experiment_dir


def main() -> None:
    """CLI entry point for single-scenario experiment execution."""
    parser = argparse.ArgumentParser(description="Run one IEEE experiment scenario")
    parser.add_argument(
        "--scenario",
        required=True,
        choices=list(SCENARIO_MAP.keys()),
        help="Experiment scenario to execute",
    )
    parser.add_argument("--output-dir", default="", help="Optional custom output directory")
    args = parser.parse_args()

    output_root = Path(args.output_dir) if args.output_dir else None
    run_experiment(args.scenario, output_root=output_root)


if __name__ == "__main__":
    main()
