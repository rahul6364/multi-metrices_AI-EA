"""Shared configuration and helpers for the IEEE experiment pipeline."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = PROJECT_ROOT / "results"
LOGS_DIR = RESULTS_ROOT / "logs"
METRICS_DIR = RESULTS_ROOT / "metrics"
FIGURES_DIR = RESULTS_ROOT / "figures"
RAW_METRICS_DIR = RESULTS_ROOT / "raw_metrics"
EXPERIMENTS_DIR = RESULTS_ROOT / "experiments"
WORKLOADS_DIR = PROJECT_ROOT / "ai-anomaly-detection" / "workloads"

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090").rstrip("/")


def _detect_detector_url() -> str:
    """Pick the first reachable detector endpoint (port-forward or NodePort)."""
    import requests

    candidates = [
        os.getenv("DETECTOR_URL", "").rstrip("/"),
        "http://localhost:8006",
        "http://localhost:30080",
    ]
    for url in candidates:
        if not url:
            continue
        try:
            response = requests.get(f"{url}/api/status", timeout=3)
            if response.status_code < 500:
                return url
        except requests.RequestException:
            continue
    return os.getenv("DETECTOR_URL", "http://localhost:8006").rstrip("/") or "http://localhost:8006"


DETECTOR_URL = _detect_detector_url()
TARGET_NAMESPACE = os.getenv("TARGET_NAMESPACE", "default")
DETECTOR_NAMESPACE = os.getenv("DETECTOR_NAMESPACE", "default")
DETECTOR_DEPLOYMENT = os.getenv("DETECTOR_DEPLOYMENT", "ai-detector")

SCENARIO_MAP = {
    "normal": {
        "label": "Normal",
        "attack_yaml": None,
        "attack_prefix": None,
    },
    "cpu": {
        "label": "CPU",
        "attack_yaml": WORKLOADS_DIR / "attack-cpu.yaml",
        "attack_prefix": "attack-cpu",
    },
    "memory": {
        "label": "Memory",
        "attack_yaml": WORKLOADS_DIR / "attack-memory.yaml",
        "attack_prefix": "attack-memory",
    },
    "network": {
        "label": "Network",
        "attack_yaml": WORKLOADS_DIR / "attack-network.yaml",
        "attack_prefix": "attack-network",
    },
    "combined": {
        "label": "Combined",
        "attack_yaml": WORKLOADS_DIR / "attack-combined.yaml",
        "attack_prefix": "attack-combined",
    },
    "cryptojacking": {
        "label": "Cryptojacking",
        "attack_yaml": WORKLOADS_DIR / "attack-cryptojacking.yaml",
        "attack_prefix": "attack-cryptojacking",
    },
}

ATTACK_YAMLS = [
    WORKLOADS_DIR / "attack-cpu.yaml",
    WORKLOADS_DIR / "attack-memory.yaml",
    WORKLOADS_DIR / "attack-network.yaml",
    WORKLOADS_DIR / "attack-combined.yaml",
    WORKLOADS_DIR / "attack-cryptojacking.yaml",
]


def ensure_result_dirs() -> None:
    """Create the standard results directory tree if missing."""
    for path in [LOGS_DIR, METRICS_DIR, FIGURES_DIR, RAW_METRICS_DIR, EXPERIMENTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)
