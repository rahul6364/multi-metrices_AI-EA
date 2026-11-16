"""
Original File: experiments/run_experiment.py
Original Entity: run_experiment and _wait_for_attack_outcome
Lines: 35–64, 99–129
Status: Implemented
Module: D.8 – Controlled Attack and Workload Simulation
"""

import time
from utils import apply_workload, detector_get, copy_detector_logs
from export_metrics import export_metrics

def _wait_for_attack_outcome(scenario: str, timeout_seconds: int = 900) -> dict:
    """Poll detector APIs until anomaly confirmation and mitigation execution occur."""
    deadline = time.time() + timeout_seconds
    summary = {"scenario": scenario, "confirmed_attack_detected": False, "mitigation_observed": False}
    while time.time() < deadline:
        detections = detector_get("/api/detections")
        mitigations = detector_get("/api/mitigations")
        if any(item.get("confirmed_attack") for item in detections):
            summary["confirmed_attack_detected"] = True
        if mitigations:
            summary["mitigation_observed"] = True
            if scenario != "normal":
                break
        time.sleep(5)
    return summary

def run_attack_simulation(scenario: str, scenario_cfg: dict, experiment_dir) -> dict:
    """Deploy controlled synthetic attack manifest and orchestrate detection verification."""
    print(f"[INFO] Deploying attack workload: {scenario_cfg['attack_yaml'].name}")
    apply_workload(scenario_cfg["attack_yaml"])
    time.sleep(20)

    # Collect attack-phase telemetry and wait for autonomous mitigation
    export_metrics(experiment_dir / "attack_metrics", namespace="default")
    summary = _wait_for_attack_outcome(scenario)
    copy_detector_logs(experiment_dir / "detector_logs")
    return summary
