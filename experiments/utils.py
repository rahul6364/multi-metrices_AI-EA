"""Utility helpers shared across experiment scripts."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import requests

from experiment_config import DETECTOR_DEPLOYMENT, DETECTOR_NAMESPACE, DETECTOR_URL


def run_cmd(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and optionally raise on failure."""
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def wait_for_http(url: str, timeout_seconds: int = 120) -> None:
    """Poll an HTTP endpoint until it responds or timeout expires."""
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:
                return
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(2)
    raise TimeoutError(f"Endpoint not ready: {url}. Last error: {last_error}")


def detector_post(path: str, timeout: int = 30) -> dict:
    """Send a POST request to the detector dashboard API."""
    response = requests.post(f"{DETECTOR_URL}{path}", timeout=timeout)
    response.raise_for_status()
    return response.json()


def detector_get(path: str, timeout: int = 30) -> dict:
    """Send a GET request to the detector dashboard API."""
    response = requests.get(f"{DETECTOR_URL}{path}", timeout=timeout)
    response.raise_for_status()
    return response.json()


def wait_for_detector_state(target_state: str, timeout_seconds: int = 900) -> None:
    """Wait until the detector reaches the requested runtime state."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status = detector_get("/api/status")
        if status.get("state") == target_state:
            return
        time.sleep(5)
    raise TimeoutError(f"Detector did not reach state '{target_state}' within {timeout_seconds}s")


def cleanup_attacks(attack_yamls: Iterable[Path]) -> None:
    """Remove all configured attack workloads from the cluster."""
    for yaml_path in attack_yamls:
        run_cmd(["kubectl", "delete", "-f", str(yaml_path), "--ignore-not-found"], check=False)


def apply_workload(yaml_path: Path) -> None:
    """Apply a Kubernetes workload manifest."""
    run_cmd(["kubectl", "apply", "-f", str(yaml_path)])


def get_detector_pod_name() -> str:
    """Return the first running ai-detector pod name."""
    result = run_cmd(
        [
            "kubectl", "get", "pods", "-n", DETECTOR_NAMESPACE,
            "-l", "app=ai-detector",
            "-o", "jsonpath={.items[0].metadata.name}",
        ]
    )
    pod_name = result.stdout.strip()
    if not pod_name:
        raise RuntimeError("No ai-detector pod found")
    return pod_name


def copy_detector_logs(destination: Path) -> None:
    """Copy research and evaluation logs from the detector pod to the host."""
    pod_name = get_detector_pod_name()
    destination.mkdir(parents=True, exist_ok=True)
    remote_files = [
        "/app/logs/evaluation.csv",
        "/app/logs/detections.csv",
        "/app/logs/mitigations.csv",
        "/app/data/raw_metrics.csv",
    ]
    for remote_path in remote_files:
        local_target = destination / Path(remote_path).name
        cmd = [
            "kubectl", "cp", "-n", DETECTOR_NAMESPACE,
            f"{pod_name}:{remote_path}",
            str(local_target),
        ]
        run_cmd(cmd, check=False)

    research_dest = destination / "research"
    research_dest.mkdir(parents=True, exist_ok=True)
    list_cmd = [
        "kubectl", "exec", "-n", DETECTOR_NAMESPACE, pod_name, "--",
        "sh", "-c", "ls /app/logs/research/*.csv 2>/dev/null || true",
    ]
    listing = run_cmd(list_cmd, check=False)
    for remote_path in listing.stdout.split():
        remote_path = remote_path.strip()
        if not remote_path:
            continue
        local_target = research_dest / Path(remote_path).name
        run_cmd(
            [
                "kubectl", "cp", "-n", DETECTOR_NAMESPACE,
                f"{pod_name}:{remote_path}",
                str(local_target),
            ],
            check=False,
        )


def validate_csv(path: Path, required_columns: Optional[list[str]] = None) -> pd.DataFrame:
    """Load and validate a CSV file, raising if empty or missing columns."""
    if not path.exists():
        raise FileNotFoundError(f"Missing CSV file: {path}")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"CSV file is empty: {path}")
    if required_columns:
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"CSV {path} missing columns: {missing}")
    return df


def save_json(path: Path, payload: dict) -> None:
    """Write a JSON document with stable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
