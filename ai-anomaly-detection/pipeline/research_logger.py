"""
Centralized research logging for IEEE experiment reproducibility.

Appends detection-cycle records to timestamped CSV files without overwriting
existing logs. Designed to run inside the ai-detector pod (/app/logs/research/)
and be copied to the host results/ directory by the experiment pipeline.
"""

from __future__ import annotations

import csv
import os
import time
from collections import defaultdict
from typing import Optional

import config


RESEARCH_LOG_COLUMNS = [
    "timestamp",
    "pod_name",
    "namespace",
    "cpu_utilization_percent",
    "memory_utilization_percent",
    "network_receive_bytes",
    "network_transmit_bytes",
    "energy_consumption_joules",
    "energy_cpu_ratio",
    "rolling_cpu_average",
    "rolling_energy_average",
    "anomaly_score",
    "prediction",
    "confidence",
    "detected_attack_type",
    "mitigation_action",
    "detection_latency_ms",
    "mitigation_latency_ms",
    "pod_status",
]

_MEMORY_REFERENCE_BYTES = 512 * 1024 * 1024


def _attack_type_from_pod(pod_name: str) -> str:
    """Map attack pod naming convention to a human-readable attack category."""
    mapping = {
        "attack-cpu": "CPU",
        "attack-memory": "Memory",
        "attack-network": "Network",
        "attack-combined": "Combined",
        "attack-cryptojacking": "Cryptojacking",
    }
    for prefix, label in mapping.items():
        if pod_name.startswith(prefix):
            return label
    return "Normal"


def _confidence_from_score(score: float) -> float:
    """Convert Isolation Forest decision score to a bounded confidence value."""
    return float(min(max(abs(score), 0.0), 1.0))


class ResearchLogger:
    """Append-only CSV logger for research-grade detection-cycle telemetry."""

    def __init__(self, log_dir: Optional[str] = None) -> None:
        self.log_dir = log_dir or getattr(config, "RESEARCH_LOG_DIR", "/app/logs/research")
        self.experiment_id = os.getenv("RESEARCH_EXPERIMENT_ID", time.strftime("%Y%m%d_%H%M%S"))
        self.log_path = os.path.join(self.log_dir, f"detection_cycles_{self.experiment_id}.csv")
        self._first_attack_sample: dict[str, float] = {}
        self._first_anomaly: dict[str, float] = {}
        self._first_mitigation: dict[str, float] = {}
        self._last_mitigation_action: dict[str, str] = defaultdict(str)
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Create the log directory and CSV header if the file does not exist."""
        os.makedirs(self.log_dir, exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", newline="", encoding="utf-8") as handle:
                csv.writer(handle).writerow(RESEARCH_LOG_COLUMNS)

    def _cpu_percent(self, cpu_cores: float) -> float:
        """Express CPU usage as percent of one full CPU core."""
        return float(max(cpu_cores, 0.0) * 100.0)

    def _memory_percent(self, memory_bytes: float) -> float:
        """Express memory usage as percent of the reference memory budget."""
        if memory_bytes <= 0:
            return 0.0
        return float(min((memory_bytes / _MEMORY_REFERENCE_BYTES) * 100.0, 100.0))

    def _update_latency_tracking(
        self,
        pod_name: str,
        sample,
        prediction: str,
        confirmed_attack: bool,
    ) -> tuple[float, float]:
        """Track first attack/anomaly timestamps and return latency fields in ms."""
        now = float(sample.timestamp)
        is_attack = bool(getattr(sample, "is_attack_pod", False) or pod_name.startswith("attack-"))

        if is_attack and pod_name not in self._first_attack_sample:
            self._first_attack_sample[pod_name] = now

        if prediction == "ANOMALY" and pod_name not in self._first_anomaly:
            self._first_anomaly[pod_name] = now

        detection_latency_ms = -1.0
        if pod_name in self._first_attack_sample and pod_name in self._first_anomaly:
            detection_latency_ms = (
                self._first_anomaly[pod_name] - self._first_attack_sample[pod_name]
            ) * 1000.0

        mitigation_latency_ms = -1.0
        if confirmed_attack and pod_name in self._first_anomaly:
            if pod_name in self._first_mitigation:
                mitigation_latency_ms = (
                    self._first_mitigation[pod_name] - self._first_anomaly[pod_name]
                ) * 1000.0

        return detection_latency_ms, mitigation_latency_ms

    def log_detection_cycle(self, sample, feature_dict: dict, result) -> None:
        """Record one detection cycle with resource, model, and latency metadata."""
        detection_latency_ms, mitigation_latency_ms = self._update_latency_tracking(
            result.pod_name,
            sample,
            result.prediction_ea,
            result.confirmed_attack,
        )

        row = {
            "timestamp": sample.timestamp,
            "pod_name": result.pod_name,
            "namespace": sample.namespace,
            "cpu_utilization_percent": self._cpu_percent(feature_dict.get("avg_cpu", 0.0)),
            "memory_utilization_percent": self._memory_percent(sample.memory_bytes),
            "network_receive_bytes": float(sample.network_rx_bytes_per_sec),
            "network_transmit_bytes": float(sample.network_tx_bytes_per_sec),
            "energy_consumption_joules": float(feature_dict.get("avg_energy", 0.0)),
            "energy_cpu_ratio": float(feature_dict.get("energy_cpu_ratio", 0.0)),
            "rolling_cpu_average": float(feature_dict.get("avg_cpu", 0.0)),
            "rolling_energy_average": float(feature_dict.get("avg_energy", 0.0)),
            "anomaly_score": float(result.score_ea),
            "prediction": result.prediction_ea,
            "confidence": _confidence_from_score(result.score_ea),
            "detected_attack_type": _attack_type_from_pod(result.pod_name),
            "mitigation_action": self._last_mitigation_action.get(result.pod_name, ""),
            "detection_latency_ms": detection_latency_ms,
            "mitigation_latency_ms": mitigation_latency_ms,
            "pod_status": "Running",
        }

        with open(self.log_path, "a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=RESEARCH_LOG_COLUMNS)
            writer.writerow(row)

    def log_mitigation_event(self, pod_name: str, action: str, timestamp: Optional[float] = None) -> None:
        """Record mitigation timing and update the latest action for a pod."""
        event_time = timestamp or time.time()
        self._last_mitigation_action[pod_name] = action
        if pod_name not in self._first_mitigation:
            self._first_mitigation[pod_name] = event_time

        event_path = os.path.join(self.log_dir, f"mitigation_events_{self.experiment_id}.csv")
        write_header = not os.path.exists(event_path)
        with open(event_path, "a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            if write_header:
                writer.writerow(["timestamp", "pod_name", "mitigation_action"])
            writer.writerow([event_time, pod_name, action])
